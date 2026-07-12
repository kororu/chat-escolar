import { useCallback, useEffect, useState } from 'react'
import './App.css'

const API_BASE_URL = 'http://127.0.0.1:8000'
const ACTIVE_PROFILE_KEY = 'chat-escolar-active-profile-id'

const courses = ['1° básico', '5° básico', '6° básico']
const roles = ['Estudiante', 'Apoderado', 'Docente']
const modes = ['Estudiar para el colegio', 'Explorar mis intereses', 'Practicar', 'Ver videos']
const subjects = ['Ciencias Naturales', 'Matemática', 'Lenguaje', 'Historia']
const quickActions = ['No entendí', 'Explícalo más fácil', 'Dame un ejemplo', 'Hazme una pregunta']

const backendLabels = {
  checking: 'Comprobando backend...',
  connected: 'Backend conectado',
  unavailable: 'Backend no disponible',
}

function greetingFor(profile) {
  if (profile.role === 'Apoderado') {
    return `Hola, ${profile.name}. ¿Qué tema quieres preparar para explicar?`
  }
  if (profile.role === 'Docente') {
    return `Hola, profesora/profesor ${profile.name}. ¿Qué tema quieres trabajar?`
  }
  return `Hola, ${profile.name}. ¿Qué quieres aprender hoy?`
}

function responsePrefix(profile) {
  if (profile.role === 'Apoderado') {
    return `Claro, ${profile.name}. Te explico una forma simple para enseñárselo al estudiante.`
  }
  if (profile.role === 'Docente') {
    return `Claro, ${profile.name}. Puedes trabajarlo con una explicación breve y una actividad simple.`
  }
  return `Claro, ${profile.name}. Vamos paso a paso.`
}

function SelectionGroup({ title, options, selected, onSelect }) {
  return (
    <section className="control-group" aria-label={title}>
      <h2>{title}</h2>
      <div className="option-grid">
        {options.map((option) => (
          <button
            className={selected === option ? 'option selected' : 'option'}
            key={option}
            type="button"
            onClick={() => onSelect(option)}
          >
            {option}
          </button>
        ))}
      </div>
    </section>
  )
}

function ProfileScreen({ profiles, onCreate, onSelect, backendStatus, activeProfile }) {
  const [name, setName] = useState('')
  const [role, setRole] = useState('Estudiante')
  const [course, setCourse] = useState('5° básico')
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState('')

  const submitProfile = async (event) => {
    event.preventDefault()
    if (!name.trim() || isSaving) return

    setIsSaving(true)
    setError('')
    try {
      await onCreate({ name: name.trim(), role, course })
    } catch {
      setError('No pude guardar el perfil. Revisa que el backend esté conectado.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <main className="welcome-shell">
      <section className="welcome-card">
        <div className="welcome-copy">
          <p className="eyebrow">Tutor educativo local</p>
          <h1>{activeProfile ? 'Cambiar perfil' : 'Bienvenido a Chat Escolar'}</h1>
          <p className="welcome-subtitle">Aprende paso a paso</p>
          <p className="welcome-note">
            Crea un perfil local para adaptar el saludo y la forma de explicar. No necesitas contraseña.
          </p>
          <span className={`backend-status ${backendStatus}`}>{backendLabels[backendStatus]}</span>
        </div>

        <form className="profile-form" onSubmit={submitProfile}>
          <h2>Tu perfil</h2>
          <label htmlFor="profile-name">Nombre</label>
          <input
            id="profile-name"
            maxLength="80"
            placeholder="Ej: Ariel"
            required
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
          <label htmlFor="profile-role">Tipo de usuario</label>
          <select id="profile-role" value={role} onChange={(event) => setRole(event.target.value)}>
            {roles.map((item) => <option key={item}>{item}</option>)}
          </select>
          <label htmlFor="profile-course">Curso asociado</label>
          <select id="profile-course" value={course} onChange={(event) => setCourse(event.target.value)}>
            {courses.map((item) => <option key={item}>{item}</option>)}
          </select>
          {error && <p className="form-error">{error}</p>}
          <button className="primary-button" disabled={isSaving} type="submit">
            {isSaving ? 'Guardando...' : 'Comenzar'}
          </button>
        </form>

        {profiles.length > 0 && (
          <section className="saved-profiles" aria-label="Perfiles guardados">
            <h2>O usa un perfil guardado</h2>
            <div className="profile-list">
              {profiles.map((profile) => (
                <button key={profile.id} type="button" onClick={() => onSelect(profile)}>
                  <strong>{profile.name}</strong>
                  <span>{profile.role} · {profile.course}</span>
                </button>
              ))}
            </div>
          </section>
        )}
      </section>
    </main>
  )
}

function App() {
  const [backendStatus, setBackendStatus] = useState('checking')
  const [profiles, setProfiles] = useState([])
  const [activeProfile, setActiveProfile] = useState(null)
  const [showProfileScreen, setShowProfileScreen] = useState(true)
  const [course, setCourse] = useState('5° básico')
  const [mode, setMode] = useState('Estudiar para el colegio')
  const [subject, setSubject] = useState('Ciencias Naturales')
  const [question, setQuestion] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [historyItems, setHistoryItems] = useState([])
  const [historyError, setHistoryError] = useState('')
  const [messages, setMessages] = useState([])
  const latestHistory = historyItems[0]

  const activateProfile = useCallback(async (profile) => {
    localStorage.setItem(ACTIVE_PROFILE_KEY, String(profile.id))
    setActiveProfile(profile)
    setCourse(profile.course)
    setMessages([{ from: 'assistant', text: greetingFor(profile) }])
    setShowProfileScreen(false)
    try {
      await fetch(`${API_BASE_URL}/profiles/${profile.id}/last-used`, { method: 'PATCH' })
    } catch {
      // El perfil sigue disponible localmente aunque falle esta marca auxiliar.
    }
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    const initialize = async () => {
      try {
        const [healthResponse, profilesResponse] = await Promise.all([
          fetch(`${API_BASE_URL}/health`, { signal: controller.signal }),
          fetch(`${API_BASE_URL}/profiles`, { signal: controller.signal }),
        ])
        const health = await healthResponse.json()
        const profileData = await profilesResponse.json()
        const loadedProfiles = profileData.items ?? []
        setProfiles(loadedProfiles)
        setBackendStatus(healthResponse.ok && health.status === 'ok' ? 'connected' : 'unavailable')

        const savedId = Number(localStorage.getItem(ACTIVE_PROFILE_KEY))
        const savedProfile = loadedProfiles.find((profile) => profile.id === savedId)
        if (savedProfile) await activateProfile(savedProfile)
      } catch (error) {
        if (error.name !== 'AbortError') setBackendStatus('unavailable')
      }
    }
    initialize()
    return () => controller.abort()
  }, [activateProfile])

  const loadHistory = useCallback(async () => {
    if (!activeProfile) return
    try {
      const response = await fetch(`${API_BASE_URL}/history?profile_id=${activeProfile.id}`)
      if (!response.ok) throw new Error('History request failed')
      const data = await response.json()
      setHistoryItems(data.items ?? [])
      setHistoryError('')
      setBackendStatus('connected')
    } catch {
      setHistoryError('No pude cargar el historial')
      setBackendStatus('unavailable')
    }
  }, [activeProfile])

  useEffect(() => {
    const timer = window.setTimeout(loadHistory, 0)
    return () => window.clearTimeout(timer)
  }, [loadHistory])

  const createProfile = async (profileData) => {
    const response = await fetch(`${API_BASE_URL}/profiles`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profileData),
    })
    if (!response.ok) throw new Error('Profile request failed')
    const data = await response.json()
    setProfiles((current) => [data.profile, ...current])
    setBackendStatus('connected')
    await activateProfile(data.profile)
  }

  const resetLocalProfile = () => {
    localStorage.removeItem(ACTIVE_PROFILE_KEY)
    setActiveProfile(null)
    setMessages([])
    setHistoryItems([])
    setShowProfileScreen(true)
  }

  const fetchDemoAnswer = async (cleanQuestion) => {
    const response = await fetch(`${API_BASE_URL}/chat/demo`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        course,
        mode,
        subject,
        question: cleanQuestion,
        profile_id: activeProfile.id,
        user_name: activeProfile.name,
        user_role: activeProfile.role,
      }),
    })
    if (!response.ok) throw new Error('Demo tutor request failed')
    return response.json()
  }

  const sendQuestion = async () => {
    const cleanQuestion = question.trim()
    if (!cleanQuestion || isSending) return
    setQuestion('')
    setIsSending(true)
    setMessages((current) => [...current, { from: 'student', text: cleanQuestion }])
    try {
      const data = await fetchDemoAnswer(cleanQuestion)
      setMessages((current) => [...current, { from: 'assistant', text: data.answer, summary: data.summary }])
      setBackendStatus(data.status === 'ok' ? 'connected' : 'unavailable')
      await loadHistory()
    } catch {
      setMessages((current) => [...current, { from: 'assistant', text: 'No pude conectar con el tutor demo.' }])
      setBackendStatus('unavailable')
    } finally {
      setIsSending(false)
    }
  }

  const handleQuickAction = (action) => {
    const detail = action === 'Dame un ejemplo'
      ? 'Si estudiamos fracciones, 1/2 significa una parte de dos partes iguales.'
      : action === 'Hazme una pregunta'
        ? 'Pregunta de práctica: ¿Cuál es el lugar donde vive un ser vivo?'
        : 'Un hábitat es la casa natural de un ser vivo. ¿El agua puede ser el hábitat de un pez?'
    setMessages((current) => [
      ...current,
      { from: 'student', text: action },
      { from: 'assistant', text: `${responsePrefix(activeProfile)}\n\n${detail}` },
    ])
  }

  const updateLatestStatus = async () => {
    if (!latestHistory) return
    const nextStatus = latestHistory.status === 'pendiente' ? 'leido' : 'pendiente'
    try {
      const response = await fetch(`${API_BASE_URL}/history/${latestHistory.id}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: nextStatus }),
      })
      if (!response.ok) throw new Error('Status update failed')
      await loadHistory()
    } catch {
      setHistoryError('No pude actualizar el estado')
    }
  }

  const toggleLatestFavorite = async () => {
    if (!latestHistory) return
    try {
      const response = await fetch(`${API_BASE_URL}/history/${latestHistory.id}/favorite`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_favorite: !latestHistory.is_favorite }),
      })
      if (!response.ok) throw new Error('Favorite update failed')
      await loadHistory()
    } catch {
      setHistoryError('No pude actualizar el favorito')
    }
  }

  const continueLatestHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/history/continue?profile_id=${activeProfile.id}`)
      if (!response.ok) throw new Error('Continue request failed')
      const data = await response.json()
      if (!data.item) {
        setHistoryError('Todavía no hay historial para continuar')
        return
      }
      setCourse(data.item.course)
      setMode(data.item.mode)
      setSubject(data.item.subject)
      setMessages((current) => [
        ...current,
        { from: 'student', text: data.item.question },
        { from: 'assistant', text: data.item.answer_full, summary: data.item.answer_summary },
      ])
      setHistoryError('')
    } catch {
      setHistoryError('No pude continuar el historial')
    }
  }

  if (showProfileScreen || !activeProfile) {
    return (
      <ProfileScreen
        activeProfile={activeProfile}
        backendStatus={backendStatus}
        onCreate={createProfile}
        onSelect={activateProfile}
        profiles={profiles}
      />
    )
  }

  return (
    <main className="app-shell">
      <section className="intro">
        <div>
          <p className="eyebrow">Tutor educativo inclusivo</p>
          <h1>Chat Escolar</h1>
          <p className="subtitle">{greetingFor(activeProfile)}</p>
        </div>
        <div className="student-card" aria-label="Perfil actual">
          <span className={`backend-status ${backendStatus}`}>{backendLabels[backendStatus]}</span>
          <span>Perfil activo</span>
          <strong>{activeProfile.name}</strong>
          <small>{activeProfile.role} · {activeProfile.course}</small>
          <div className="profile-actions">
            <button type="button" onClick={() => setShowProfileScreen(true)}>Cambiar perfil</button>
            <button className="danger-link" type="button" onClick={resetLocalProfile}>Borrar perfil local</button>
          </div>
        </div>
      </section>

      <section className="mascot-placeholder" aria-label="Espacio para futura mascota">
        <div className="mascot-avatar" aria-hidden="true">CE</div>
        <div>
          <strong>Mascota pendiente</strong>
          <p>¡Hola, {activeProfile.name}! Estoy lista para acompañarte.</p>
        </div>
      </section>

      <section className="workspace">
        <aside className="selectors" aria-label="Configuración del estudio">
          <SelectionGroup title="Curso" options={courses} selected={course} onSelect={setCourse} />
          <SelectionGroup title="Modo" options={modes} selected={mode} onSelect={setMode} />
          <SelectionGroup title="Materia" options={subjects} selected={subject} onSelect={setSubject} />
        </aside>

        <section className="chat-panel" aria-label="Chat simulado">
          <header className="chat-header">
            <div><span>{course}</span><strong>{subject}</strong></div>
            <p>{mode}</p>
          </header>
          <div className="messages">
            {messages.map((message, index) => (
              <article className={`message ${message.from}`} key={`${message.from}-${index}`}>
                <span>{message.from === 'assistant' ? 'Chat Escolar' : activeProfile.name}</span>
                <p>{message.text}</p>
                {message.summary && <small className="message-summary">Resumen: {message.summary}</small>}
              </article>
            ))}
          </div>
          <div className="quick-actions" aria-label="Botones rápidos">
            {quickActions.map((action) => (
              <button key={action} type="button" onClick={() => handleQuickAction(action)}>{action}</button>
            ))}
          </div>
          <form className="question-form" onSubmit={(event) => { event.preventDefault(); sendQuestion() }}>
            <label htmlFor="question">Escribe una pregunta</label>
            <div>
              <input id="question" value={question} placeholder="Ej: ¿Qué es un hábitat?" onChange={(event) => setQuestion(event.target.value)} />
              <button type="submit" disabled={isSending}>{isSending ? 'Enviando...' : 'Enviar'}</button>
            </div>
          </form>
        </section>

        <aside className="side-panel">
          <section className="history-card" aria-label="Historial simple">
            <div className="section-title">
              <h2>Historial de {activeProfile.name}</h2>
              <div className="history-actions">
                <button type="button" disabled={!latestHistory} onClick={updateLatestStatus}>
                  Marcar {latestHistory?.status === 'pendiente' ? 'leído' : 'pendiente'}
                </button>
                <button type="button" disabled={!latestHistory} onClick={toggleLatestFavorite}>
                  {latestHistory?.is_favorite ? 'Quitar favorito' : 'Favorito'}
                </button>
              </div>
            </div>
            <dl>
              <div><dt>Última pregunta</dt><dd>{latestHistory?.question ?? 'Sin preguntas guardadas todavía'}</dd></div>
              <div><dt>Resumen</dt><dd>{latestHistory?.answer_summary ?? 'El resumen aparecerá al usar el tutor demo.'}</dd></div>
              <div><dt>Estado</dt><dd><span className={`status ${latestHistory?.status ?? 'pendiente'}`}>{latestHistory?.status ?? 'pendiente'}</span></dd></div>
              <div><dt>Favorito</dt><dd>{latestHistory?.is_favorite ? 'Sí' : 'No'}</dd></div>
            </dl>
            {historyError && <p className="history-error">{historyError}</p>}
            <button className="continue-button" type="button" disabled={!latestHistory} onClick={continueLatestHistory}>Continuar donde quedé</button>
          </section>

          <section className="videos" aria-label="Videos recomendados">
            <h2>Videos recomendados</h2>
            <div className="video-card">
              <div className="video-thumb" aria-hidden="true">▶</div>
              <div><h3>Hábitats y ecosistemas</h3><p>Canal educativo sugerido</p><small>6 min · Ideas clave con ejemplos.</small></div>
            </div>
          </section>
        </aside>
      </section>
    </main>
  )
}

export default App
