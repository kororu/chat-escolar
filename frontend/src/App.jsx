import { useCallback, useEffect, useState } from 'react'
import './App.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

const courses = ['1° básico', '5° básico', '6° básico']
const modes = [
  'Estudiar para el colegio',
  'Explorar mis intereses',
  'Practicar',
  'Ver videos',
]
const subjects = ['Ciencias Naturales', 'Matemática', 'Lenguaje', 'Historia']
const quickActions = [
  'No entendí',
  'Explícalo más fácil',
  'Dame un ejemplo',
  'Hazme una pregunta',
]

const videoCards = [
  {
    title: 'Hábitats y ecosistemas',
    source: 'Canal educativo sugerido',
    time: '6 min',
    note: 'Ideas clave con ejemplos de animales y plantas.',
  },
  {
    title: 'Fracciones paso a paso',
    source: 'Lista curada para estudiar',
    time: '8 min',
    note: 'Apoyo visual para numerador y denominador.',
  },
]

const backendLabels = {
  checking: 'Comprobando backend...',
  connected: 'Backend conectado',
  unavailable: 'Backend no disponible',
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

function App() {
  const [backendStatus, setBackendStatus] = useState('checking')
  const [course, setCourse] = useState('5° básico')
  const [mode, setMode] = useState('Estudiar para el colegio')
  const [subject, setSubject] = useState('Ciencias Naturales')
  const [question, setQuestion] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [historyItems, setHistoryItems] = useState([])
  const [historyError, setHistoryError] = useState('')
  const [messages, setMessages] = useState([
    {
      from: 'student',
      text: 'No entiendo qué es un hábitat.',
    },
    {
      from: 'assistant',
      text:
        'No te preocupes. Vamos paso a paso.\n\nExplicación corta:\nUn hábitat es el lugar donde vive un ser vivo.\n\nEjemplo:\nUn pez vive en el agua. Un cactus vive en el desierto.\n\nMini resumen:\nEl hábitat es el hogar natural de un ser vivo.\n\nPregunta:\n¿Dónde vive un pez?',
    },
  ])
  const latestHistory = historyItems[0]

  const loadHistory = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/history`)

      if (!response.ok) {
        throw new Error('History request failed')
      }

      const data = await response.json()
      setHistoryItems(data.items ?? [])
      setHistoryError('')
      setBackendStatus('connected')
    } catch {
      setHistoryError('No pude cargar el historial')
      setBackendStatus('unavailable')
    }
  }, [])

  useEffect(() => {
    const controller = new AbortController()

    const checkBackend = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/health`, {
          signal: controller.signal,
        })
        const data = await response.json()

        setBackendStatus(response.ok && data.status === 'ok' ? 'connected' : 'unavailable')
      } catch (error) {
        if (error.name !== 'AbortError') {
          setBackendStatus('unavailable')
        }
      }
    }

    checkBackend()

    return () => controller.abort()
  }, [])

  useEffect(() => {
    const timer = window.setTimeout(loadHistory, 0)

    return () => window.clearTimeout(timer)
  }, [loadHistory])

  const fetchDemoAnswer = async (cleanQuestion) => {
    const response = await fetch(`${API_BASE_URL}/chat/demo`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        course,
        mode,
        subject,
        question: cleanQuestion,
      }),
    })

    if (!response.ok) {
      throw new Error('Demo tutor request failed')
    }

    return response.json()
  }

  const sendQuestion = async () => {
    const cleanQuestion = question.trim()

    if (!cleanQuestion || isSending) {
      return
    }

    setQuestion('')
    setIsSending(true)
    setMessages((currentMessages) => [
      ...currentMessages,
      { from: 'student', text: cleanQuestion },
    ])

    try {
      const data = await fetchDemoAnswer(cleanQuestion)

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          from: 'assistant',
          text: data.answer,
          summary: data.summary,
        },
      ])
      setBackendStatus(data.status === 'ok' ? 'connected' : 'unavailable')
      loadHistory()
    } catch {
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          from: 'assistant',
          text: 'No pude conectar con el tutor demo',
        },
      ])
      setBackendStatus('unavailable')
    } finally {
      setIsSending(false)
    }
  }

  const handleQuickAction = (action) => {
    setMessages((currentMessages) => [
      ...currentMessages,
      { from: 'student', text: action },
      {
        from: 'assistant',
        text:
          action === 'Dame un ejemplo'
            ? 'Ejemplo:\nSi estudiamos fracciones, 1/2 significa una parte de dos partes iguales.'
            : action === 'Hazme una pregunta'
              ? 'Pregunta de práctica:\n¿Cuál es el lugar donde vive un ser vivo?'
              : 'No te preocupes. Lo vemos más fácil.\n\nUn hábitat es la casa natural de un ser vivo.\n\nPregunta:\n¿El agua puede ser el hábitat de un pez?',
      },
    ])
  }

  const updateLatestStatus = async () => {
    if (!latestHistory) {
      return
    }

    const nextStatus = latestHistory.status === 'pendiente' ? 'leido' : 'pendiente'

    try {
      const response = await fetch(`${API_BASE_URL}/history/${latestHistory.id}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: nextStatus }),
      })

      if (!response.ok) {
        throw new Error('Status update failed')
      }

      await loadHistory()
    } catch {
      setHistoryError('No pude actualizar el estado')
      setBackendStatus('unavailable')
    }
  }

  const toggleLatestFavorite = async () => {
    if (!latestHistory) {
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/history/${latestHistory.id}/favorite`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_favorite: !latestHistory.is_favorite }),
      })

      if (!response.ok) {
        throw new Error('Favorite update failed')
      }

      await loadHistory()
    } catch {
      setHistoryError('No pude actualizar el favorito')
      setBackendStatus('unavailable')
    }
  }

  const continueLatestHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/history/continue`)

      if (!response.ok) {
        throw new Error('Continue request failed')
      }

      const data = await response.json()

      if (!data.item) {
        setHistoryError('Todavía no hay historial para continuar')
        return
      }

      setCourse(data.item.course)
      setMode(data.item.mode)
      setSubject(data.item.subject)
      setMessages((currentMessages) => [
        ...currentMessages,
        { from: 'student', text: data.item.question },
        {
          from: 'assistant',
          text: data.item.answer_full,
          summary: data.item.answer_summary,
        },
      ])
      setHistoryError('')
      setBackendStatus('connected')
      await loadHistory()
    } catch {
      setHistoryError('No pude continuar el historial')
      setBackendStatus('unavailable')
    }
  }

  return (
    <main className="app-shell">
      <section className="intro">
        <div>
          <p className="eyebrow">Tutor educativo inclusivo</p>
          <h1>Chat Escolar</h1>
          <p className="subtitle">Aprende paso a paso</p>
        </div>
        <div className="student-card" aria-label="Perfil actual">
          <span className={`backend-status ${backendStatus}`}>
            {backendLabels[backendStatus]}
          </span>
          <span>Perfil de prueba</span>
          <strong>{course}</strong>
          <small>Tutor paciente · lectura clara</small>
        </div>
      </section>

      <section className="workspace">
        <aside className="selectors" aria-label="Configuración del estudio">
          <SelectionGroup
            title="Curso"
            options={courses}
            selected={course}
            onSelect={setCourse}
          />
          <SelectionGroup
            title="Modo"
            options={modes}
            selected={mode}
            onSelect={setMode}
          />
          <SelectionGroup
            title="Materia"
            options={subjects}
            selected={subject}
            onSelect={setSubject}
          />
        </aside>

        <section className="chat-panel" aria-label="Chat simulado">
          <header className="chat-header">
            <div>
              <span>{course}</span>
              <strong>{subject}</strong>
            </div>
            <p>{mode}</p>
          </header>

          <div className="messages">
            {messages.map((message, index) => (
              <article className={`message ${message.from}`} key={`${message.from}-${index}`}>
                <span>{message.from === 'assistant' ? 'Chat Escolar' : 'Estudiante'}</span>
                <p>{message.text}</p>
                {message.summary && (
                  <small className="message-summary">Resumen: {message.summary}</small>
                )}
              </article>
            ))}
          </div>

          <div className="quick-actions" aria-label="Botones rápidos">
            {quickActions.map((action) => (
              <button key={action} type="button" onClick={() => handleQuickAction(action)}>
                {action}
              </button>
            ))}
          </div>

          <form
            className="question-form"
            onSubmit={(event) => {
              event.preventDefault()
              sendQuestion()
            }}
          >
            <label htmlFor="question">Escribe una pregunta</label>
            <div>
              <input
                id="question"
                type="text"
                value={question}
                placeholder="Ej: ¿Qué es una cadena alimentaria?"
                onChange={(event) => setQuestion(event.target.value)}
              />
              <button type="submit" disabled={isSending}>
                {isSending ? 'Enviando...' : 'Enviar'}
              </button>
            </div>
          </form>
        </section>

        <aside className="side-panel">
          <section className="history-card" aria-label="Historial simple">
            <div className="section-title">
              <h2>Historial</h2>
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
              <div>
                <dt>Última pregunta</dt>
                <dd>{latestHistory?.question ?? 'Sin preguntas guardadas todavía'}</dd>
              </div>
              <div>
                <dt>Resumen</dt>
                <dd>{latestHistory?.answer_summary ?? 'El resumen aparecerá al usar el tutor demo.'}</dd>
              </div>
              <div>
                <dt>Estado</dt>
                <dd>
                  <span className={`status ${latestHistory?.status ?? 'pendiente'}`}>
                    {latestHistory?.status ?? 'pendiente'}
                  </span>
                </dd>
              </div>
              <div>
                <dt>Favorito</dt>
                <dd>{latestHistory?.is_favorite ? 'Sí' : 'No'}</dd>
              </div>
            </dl>
            {historyError && <p className="history-error">{historyError}</p>}
            <button
              className="continue-button"
              type="button"
              disabled={!latestHistory}
              onClick={continueLatestHistory}
            >
              Continuar donde quedé
            </button>
          </section>

          <section className="videos" aria-label="Videos recomendados">
            <h2>Videos recomendados</h2>
            <div className="video-list">
              {videoCards.map((video) => (
                <article className="video-card" key={video.title}>
                  <div className="video-thumb" aria-hidden="true">
                    ▶
                  </div>
                  <div>
                    <h3>{video.title}</h3>
                    <p>{video.source}</p>
                    <small>{video.time} · {video.note}</small>
                  </div>
                </article>
              ))}
            </div>
          </section>
        </aside>
      </section>
    </main>
  )
}

export default App
