import { useCallback, useEffect, useState } from 'react'
import './App.css'
import { APP_INFO } from './config/appInfo'
import { getNexoVariant, pickNexoVariantForSubject } from './assets/nexo/nexoVariants'
import { AssistantMessageBubble, UserMessageBubble } from './components/ChatBubbles'
import { NexoAvatar } from './components/NexoAvatar'
import { UserAvatar } from './components/UserAvatar'

const API_BASE_URL = 'http://127.0.0.1:8000'
const ACTIVE_PROFILE_KEY = 'chat-escolar-active-profile-id'
const MAX_AVATAR_SIZE_BYTES = 2 * 1024 * 1024
const AVATAR_TYPES = ['image/png', 'image/jpeg', 'image/webp']

function profileWithAvatarUrl(profile) {
  if (!profile) return profile
  return {
    ...profile,
    avatarUrl: profile.avatar_url ? `${API_BASE_URL}${profile.avatar_url}` : null,
  }
}

function conversationStorageKey(profileId) {
  return `chat-escolar-conversation-${profileId}`
}

function createConversationId() {
  if (window.crypto?.randomUUID) return window.crypto.randomUUID()
  return `conversation-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

const profileCourses = ['1° básico', '2° básico', '3° básico', '4° básico', '5° básico', '6° básico', '7° básico', '8° básico']
const ALL_COURSES = 'Todos los cursos'
const studyCourses = [...profileCourses, ALL_COURSES]
const roles = ['Estudiante', 'Apoderado', 'Docente']
const modes = ['Estudiar para el colegio', 'Explorar mis intereses', 'Practicar', 'Ver videos']
const subjects = ['Ciencias Naturales', 'Matemática', 'Lenguaje', 'Historia']
const quickActions = ['No entendí', 'Explícalo más fácil', 'Dame un ejemplo', 'Hazme una pregunta']
const videoTopics = [
  { topic: 'segunda guerra mundial', aliases: ['segunda guerra mundial', 'segunda guerra'] },
  { topic: 'comprension lectora', aliases: ['comprension lectora', 'comprender un texto'] },
  { topic: 'agujeros negros', aliases: ['agujeros negros', 'agujero negro'] },
  { topic: 'naves espaciales', aliases: ['naves espaciales', 'nave espacial'] },
  { topic: 'ecosistemas', aliases: ['ecosistemas', 'ecosistema'] },
  { topic: 'fracciones', aliases: ['fracciones', 'fraccion'] },
  { topic: 'habitat', aliases: ['habitat'] },
  { topic: 'tanques', aliases: ['tanques', 'tanque'] },
]

const backendLabels = {
  checking: 'Comprobando backend...',
  connected: 'Backend conectado',
  unavailable: 'Backend no disponible',
}

const provenanceLabels = {
  ollama_with_local_content: 'Explicado con IA local usando contenido local verificado.',
  ollama_generated: 'Explicación general de IA local, sin fuente local verificada.',
  ollama_unavailable: 'IA local no disponible: se usó el modo básico.',
  local_content_fallback: 'Se utilizó el contenido local porque la IA local no respondió.',
  local_related: 'Tema relacionado encontrado: no es una fuente principal.',
  local_low_confidence: 'Coincidencia local de baja confianza: no se usó como fuente.',
  demo_fallback: 'Usé el modo básico porque la IA local no respondió.',
  clarification_required: 'Necesito una aclaración para buscar el tema correcto.',
  no_local_content: 'Contenido local verificado no disponible para este tema.',
}

function normalizeSearchText(text) {
  return text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
}

function detectVideoTopic(question) {
  const normalizedQuestion = normalizeSearchText(question)
  return videoTopics.find(({ aliases }) => (
    aliases.some((alias) => normalizedQuestion.includes(alias))
  ))?.topic ?? null
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

function historyTitleFor(role) {
  if (role === 'Apoderado') return 'Temas consultados'
  if (role === 'Docente') return 'Temas trabajados'
  return 'Tus últimas preguntas'
}

function formatHistoryDate(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Fecha no disponible'
  return new Intl.DateTimeFormat('es-CL', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(date)
}

function formatProcessingTime(milliseconds) {
  if (!Number.isFinite(milliseconds) || milliseconds < 0) return null
  const seconds = (milliseconds / 1000).toLocaleString('es-CL', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  })
  return milliseconds >= 30000
    ? `Procesado en ${seconds} s · respuesta lenta`
    : `Procesado en ${seconds} s`
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

function SourceNotice({ message }) {
  if (message.usedLocalContent) {
    return (
      <div className="local-content-note">
        <strong>{message.provenanceStatus === 'ollama_with_local_content'
          ? 'Explicado con IA local usando contenido local'
          : 'Contenido local verificado'}</strong>
        {message.foundInOtherCourse && message.sourceCourse && (
          <small>Encontrado en otro curso: {message.sourceCourse}.</small>
        )}
        {message.provenanceStatus === 'local_content_fallback' && (
          <small>Se utilizó el contenido local porque la IA local no respondió.</small>
        )}
        {message.contentSources.length > 0 && (
          <div>
            <span>{message.contentSources.length === 1 ? 'Fuente local' : 'Fuentes locales'}</span>
            <ul>
              {message.contentSources.map((source) => (
                <li key={`${source.path}-${source.title}`}>
                  {source.title}
                  {source.course ? ` · ${source.course}` : ''}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    )
  }

  if (!message.provenanceStatus || message.provenanceStatus === 'local_verified') return null

  return (
    <div className={`provenance-note ${message.provenanceStatus}`}>
      {provenanceLabels[message.provenanceStatus] ?? 'No se usó una fuente local verificada.'}
      {message.provenanceStatus === 'local_related' && message.relatedSources?.length > 0 && (
        <small>
          Relacionado: {message.relatedSources[0].title} ({message.relatedSources[0].section})
          {message.relatedSources[0].course ? ` · ${message.relatedSources[0].course}` : ''}
        </small>
      )}
    </div>
  )
}

function AiLocalCard({ status, onTest, isTesting, testMessage }) {
  const available = status?.available && status?.model_installed
  return (
    <section className="ai-local-card" aria-label="Estado de IA local">
      <h2>IA local</h2>
      <p className={available ? 'ai-status available' : 'ai-status unavailable'}>
        {available ? 'Conectada' : 'No disponible'}
      </p>
      <small>Modelo: {status?.model ?? 'qwen3.5:2b'}</small>
      <button type="button" onClick={onTest} disabled={isTesting}>
        {isTesting ? 'Probando...' : 'Probar IA local'}
      </button>
      {testMessage && <p className="ai-test-message">{testMessage}</p>}
    </section>
  )
}

function ProcessingIndicator({ message }) {
  return (
    <div className="assistant-bubble-row processing-row" aria-busy="true" role="status">
      <NexoAvatar variant={getNexoVariant({ isProcessing: true })} size="small" />
      <article className="chat-bubble assistant-bubble processing-message">
        <span>Nexo · Procesando</span>
        <div className="processing-content">
          <i className="processing-spinner" aria-hidden="true" />
          <p>{message}</p>
          <span className="processing-dots" aria-hidden="true"><i /> <i /> <i /></span>
        </div>
      </article>
    </div>
  )
}

function ProfileScreen({ profiles, onCreate, onSelect, onDelete, onAvatarUpload, onAvatarDelete, backendStatus, activeProfile }) {
  const [name, setName] = useState('')
  const [role, setRole] = useState('Estudiante')
  const [course, setCourse] = useState('5° básico')
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState('')
  const [profileToDelete, setProfileToDelete] = useState(null)
  const [deleteError, setDeleteError] = useState('')
  const [isDeleting, setIsDeleting] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [avatarProfile, setAvatarProfile] = useState(null)
  const [avatarFile, setAvatarFile] = useState(null)
  const [avatarPreviewUrl, setAvatarPreviewUrl] = useState(null)
  const [avatarError, setAvatarError] = useState('')
  const [isSavingAvatar, setIsSavingAvatar] = useState(false)

  const closeAvatarDialog = () => {
    if (avatarPreviewUrl) URL.revokeObjectURL(avatarPreviewUrl)
    setAvatarProfile(null)
    setAvatarFile(null)
    setAvatarPreviewUrl(null)
    setAvatarError('')
  }

  const selectAvatarFile = (event) => {
    const file = event.target.files?.[0]
    if (!file) return
    if (!AVATAR_TYPES.includes(file.type)) {
      setAvatarFile(null)
      setAvatarError('Elige una imagen PNG, JPG, JPEG o WEBP.')
      return
    }
    if (file.size > MAX_AVATAR_SIZE_BYTES) {
      setAvatarFile(null)
      setAvatarError('La imagen no puede superar los 2 MB.')
      return
    }
    if (avatarPreviewUrl) URL.revokeObjectURL(avatarPreviewUrl)
    setAvatarFile(file)
    setAvatarPreviewUrl(URL.createObjectURL(file))
    setAvatarError('')
  }

  const confirmAvatar = async () => {
    if (!avatarProfile || !avatarFile || isSavingAvatar) return
    setIsSavingAvatar(true)
    setAvatarError('')
    try {
      await onAvatarUpload(avatarProfile.id, avatarFile)
      setSuccessMessage(`El avatar de ${avatarProfile.name} fue actualizado.`)
      closeAvatarDialog()
    } catch (error) {
      setAvatarError(error.message || 'No pude guardar el avatar. Inténtalo nuevamente.')
    } finally {
      setIsSavingAvatar(false)
    }
  }

  const removeAvatar = async () => {
    if (!avatarProfile || isSavingAvatar) return
    setIsSavingAvatar(true)
    setAvatarError('')
    try {
      await onAvatarDelete(avatarProfile.id)
      setSuccessMessage(`El avatar de ${avatarProfile.name} fue eliminado.`)
      closeAvatarDialog()
    } catch (error) {
      setAvatarError(error.message || 'No pude eliminar el avatar. Inténtalo nuevamente.')
    } finally {
      setIsSavingAvatar(false)
    }
  }

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

  const confirmDelete = async () => {
    if (!profileToDelete || isDeleting) return
    setIsDeleting(true)
    setDeleteError('')
    try {
      const deletedProfile = await onDelete(profileToDelete.id)
      setSuccessMessage(`El perfil ${deletedProfile.name} fue eliminado.`)
      setProfileToDelete(null)
    } catch {
      setDeleteError('No pude eliminar el perfil. Inténtalo nuevamente.')
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <main className="welcome-shell">
      <section className="welcome-card">
        <div className="welcome-copy">
          <p className="eyebrow">Tutor educativo local</p>
          <h1>{activeProfile ? 'Cambiar perfil' : `Bienvenido a ${APP_INFO.name}`}</h1>
          <p className="welcome-subtitle">Aprende paso a paso</p>
          <p className="welcome-note">
            Crea un perfil local para adaptar el saludo y la forma de explicar. No necesitas contraseña.
          </p>
          <div className="welcome-hero" aria-label="Nexo te da la bienvenida">
            <NexoAvatar variant="bienvenida" size="hero" />
            <p><strong>Hola, soy Nexo.</strong> Estoy aquí para aprender contigo.</p>
          </div>
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
            {profileCourses.map((item) => <option key={item}>{item}</option>)}
          </select>
          {error && <p className="form-error">{error}</p>}
          <button className="primary-button" disabled={isSaving} type="submit">
            {isSaving ? 'Guardando...' : 'Comenzar'}
          </button>
        </form>

        {successMessage && <p className="profile-success" role="status">{successMessage}</p>}
        {profiles.length > 0 && (
          <section className="saved-profiles" aria-label="Perfiles guardados">
            <h2>O usa un perfil guardado</h2>
            <div className="profile-list">
              {profiles.map((profile) => (
                <article className="profile-entry" key={profile.id}>
                  <button className="profile-select" type="button" onClick={() => onSelect(profile)}>
                    <UserAvatar imageUrl={profile.avatarUrl} name={profile.name} />
                    <strong>{profile.name}</strong>
                    <span>{profile.role} · {profile.course}</span>
                  </button>
                  <button
                    aria-label={`Cambiar avatar de ${profile.name}`}
                    className="avatar-profile-button"
                    type="button"
                    onClick={(event) => {
                      event.stopPropagation()
                      setSuccessMessage('')
                      setAvatarProfile(profile)
                    }}
                  >
                    Avatar
                  </button>
                  <button
                    aria-label={`Eliminar perfil ${profile.name}`}
                    className="delete-profile-button"
                    type="button"
                    onClick={(event) => {
                      event.stopPropagation()
                      setDeleteError('')
                      setSuccessMessage('')
                      setProfileToDelete(profile)
                    }}
                  >
                    Eliminar
                  </button>
                </article>
              ))}
            </div>
          </section>
        )}
      </section>
      {profileToDelete && (
        <div className="profile-modal-backdrop" role="presentation">
          <section aria-labelledby="delete-profile-title" aria-modal="true" className="profile-modal" role="dialog">
            <h2 id="delete-profile-title">¿Seguro que quieres eliminar el perfil {profileToDelete.name}?</h2>
            <p>También se eliminarán sus preguntas guardadas, favoritos, pendientes y contexto de conversación local.</p>
            {deleteError && <p className="form-error">{deleteError}</p>}
            <div className="profile-modal-actions">
              <button type="button" disabled={isDeleting} onClick={() => setProfileToDelete(null)}>Cancelar</button>
              <button className="delete-confirm-button" type="button" disabled={isDeleting} onClick={confirmDelete}>
                {isDeleting ? 'Eliminando...' : 'Eliminar perfil'}
              </button>
            </div>
          </section>
        </div>
      )}
      {avatarProfile && (
        <div className="profile-modal-backdrop" role="presentation">
          <section aria-labelledby="avatar-profile-title" aria-modal="true" className="profile-modal avatar-modal" role="dialog">
            <h2 id="avatar-profile-title">Avatar de {avatarProfile.name}</h2>
            <p>Elige una imagen local de hasta 2 MB. No se guardará hasta confirmar.</p>
            <div className="avatar-preview">
              <UserAvatar imageUrl={avatarPreviewUrl || avatarProfile.avatarUrl} name={avatarProfile.name} />
            </div>
            <label className="avatar-file-label" htmlFor="profile-avatar-file">Seleccionar imagen</label>
            <input accept="image/png,image/jpeg,image/webp" id="profile-avatar-file" onChange={selectAvatarFile} type="file" />
            {avatarError && <p className="form-error">{avatarError}</p>}
            <div className="profile-modal-actions">
              {avatarProfile.avatarUrl && !avatarFile && (
                <button className="delete-profile-button" disabled={isSavingAvatar} onClick={removeAvatar} type="button">Quitar avatar</button>
              )}
              <button disabled={isSavingAvatar} onClick={closeAvatarDialog} type="button">Cancelar</button>
              <button className="primary-button" disabled={!avatarFile || isSavingAvatar} onClick={confirmAvatar} type="button">
                {isSavingAvatar ? 'Guardando...' : 'Guardar avatar'}
              </button>
            </div>
          </section>
        </div>
      )}
    </main>
  )
}

function AboutPanel({ onClose }) {
  return (
    <div
      className="about-backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
    >
      <section
        aria-labelledby="about-title"
        aria-modal="true"
        className="about-panel"
        role="dialog"
      >
        <button
          aria-label="Cerrar Acerca de"
          autoFocus
          className="about-close"
          type="button"
          onClick={onClose}
        >
          ×
        </button>
        <p className="eyebrow">Acerca del proyecto</p>
        <h2 id="about-title">{APP_INFO.name}</h2>
        <p>{APP_INFO.description}</p>
        <dl className="about-details">
          <div><dt>Autor</dt><dd>Desarrollado por {APP_INFO.author}</dd></div>
          <div><dt>Versión</dt><dd>{APP_INFO.version}</dd></div>
          <div><dt>Año</dt><dd>{APP_INFO.year}</dd></div>
        </dl>
        <p className="about-local-note">
          Esta versión funciona localmente y no utiliza servicios de IA pagados.
        </p>
        <small>© {APP_INFO.year} — Proyecto {APP_INFO.name}</small>
      </section>
    </div>
  )
}

function App() {
  const [backendStatus, setBackendStatus] = useState('checking')
  const [profiles, setProfiles] = useState([])
  const [activeProfile, setActiveProfile] = useState(null)
  const [conversationId, setConversationId] = useState(null)
  const [showProfileScreen, setShowProfileScreen] = useState(true)
  const [course, setCourse] = useState('5° básico')
  const [mode, setMode] = useState('Estudiar para el colegio')
  const [subject, setSubject] = useState('Ciencias Naturales')
  const [question, setQuestion] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [processingMessage, setProcessingMessage] = useState('')
  const [historyItems, setHistoryItems] = useState([])
  const [historyError, setHistoryError] = useState('')
  const [historyView, setHistoryView] = useState('recent')
  const [messages, setMessages] = useState([])
  const [videos, setVideos] = useState([])
  const [videoTopic, setVideoTopic] = useState(null)
  const [videoLoadError, setVideoLoadError] = useState(false)
  const [isAboutOpen, setIsAboutOpen] = useState(false)
  const [aiStatus, setAiStatus] = useState(null)
  const [isAiTesting, setIsAiTesting] = useState(false)
  const [aiTestMessage, setAiTestMessage] = useState('')
  const latestHistory = historyItems[0]
  const pendingHistory = historyItems.filter((item) => item.status === 'pendiente')
  const favoriteHistory = historyItems.filter((item) => item.is_favorite)
  const visibleHistoryItems = historyView === 'pending'
    ? pendingHistory
    : historyView === 'favorites'
      ? favoriteHistory
      : historyItems.slice(0, 5)
  const topicVideos = videoTopic
    ? videos.filter((video) => normalizeSearchText(video.topic) === videoTopic)
    : []
  const recommendedVideos = (topicVideos.length > 0 ? topicVideos : videos).slice(0, 4)
  const courseStatusMessage = course === ALL_COURSES
    ? 'Buscando en toda la base local.'
    : activeProfile && course !== activeProfile.course
      ? `Consultando ${course} para esta pregunta.`
      : ''

  const activateProfile = useCallback(async (profile) => {
    const storageKey = conversationStorageKey(profile.id)
    const savedConversationId = localStorage.getItem(storageKey) || createConversationId()
    localStorage.setItem(storageKey, savedConversationId)
    localStorage.setItem(ACTIVE_PROFILE_KEY, String(profile.id))
    setActiveProfile(profile)
    setConversationId(savedConversationId)
    setCourse(profile.course)
    setMessages([{ from: 'assistant', text: greetingFor(profile), nexoVariant: 'bienvenida' }])
    setHistoryView('recent')
    setHistoryItems([])
    setHistoryError('')
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
        const loadedProfiles = (profileData.items ?? []).map(profileWithAvatarUrl)
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

  useEffect(() => {
    const controller = new AbortController()
    const loadVideos = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/videos`, { signal: controller.signal })
        if (!response.ok) throw new Error('Videos request failed')
        const data = await response.json()
        setVideos(Array.isArray(data) ? data : [])
        setVideoLoadError(false)
      } catch (error) {
        if (error.name !== 'AbortError') {
          setVideos([])
          setVideoLoadError(true)
        }
      }
    }
    loadVideos()
    return () => controller.abort()
  }, [])

  const loadAiStatus = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/status`)
      if (!response.ok) throw new Error('AI status request failed')
      setAiStatus(await response.json())
    } catch {
      setAiStatus({ available: false, model_installed: false, model: 'qwen3.5:2b' })
    }
  }, [])

  useEffect(() => { loadAiStatus() }, [loadAiStatus])

  useEffect(() => {
    if (!isAboutOpen) return undefined

    const closeWithEscape = (event) => {
      if (event.key === 'Escape') setIsAboutOpen(false)
    }
    document.addEventListener('keydown', closeWithEscape)
    return () => document.removeEventListener('keydown', closeWithEscape)
  }, [isAboutOpen])

  useEffect(() => {
    if (!isSending) {
      setProcessingMessage('')
      return undefined
    }

    const usingLocalAi = aiStatus?.available && aiStatus?.model_installed
    setProcessingMessage(usingLocalAi
      ? 'IA local trabajando. Puede tardar unos segundos.'
      : 'Preparando respuesta... Esto puede tardar unos segundos.')
    const sourceTimer = window.setTimeout(() => setProcessingMessage('Buscando contenidos locales y revisando fuentes disponibles...'), 1600)
    const clarityTimer = window.setTimeout(() => setProcessingMessage(usingLocalAi
      ? 'Consultando IA local y preparando una explicación clara...'
      : 'Preparando una explicación clara...'), 3600)
    const slowTimer = window.setTimeout(() => setProcessingMessage('La IA local está tardando un poco más de lo normal. El computador sigue procesando.'), 10000)
    const verySlowTimer = window.setTimeout(() => setProcessingMessage('Sigue procesando. En equipos modestos, algunas respuestas pueden tardar más.'), 30000)

    return () => {
      window.clearTimeout(sourceTimer)
      window.clearTimeout(clarityTimer)
      window.clearTimeout(slowTimer)
      window.clearTimeout(verySlowTimer)
    }
  }, [aiStatus, isSending])

  const loadHistory = useCallback(async () => {
    if (!activeProfile) return
    try {
      const response = await fetch(`${API_BASE_URL}/history?profile_id=${activeProfile.id}&limit=50`)
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
    const profile = profileWithAvatarUrl(data.profile)
    setProfiles((current) => [profile, ...current])
    setBackendStatus('connected')
    await activateProfile(profile)
  }

  const updateProfileAvatar = async (profileId, file) => {
    const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/avatar`, {
      method: 'POST',
      headers: {
        'Content-Type': file.type,
        'X-Avatar-Filename': file.name,
      },
      body: file,
    })
    const data = await response.json().catch(() => ({}))
    if (!response.ok) throw new Error(data.detail || 'No pude guardar el avatar.')
    const profile = profileWithAvatarUrl(data.profile)
    setProfiles((current) => current.map((item) => item.id === profileId ? profile : item))
    if (activeProfile?.id === profileId) setActiveProfile(profile)
    return profile
  }

  const deleteProfileAvatar = async (profileId) => {
    const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/avatar`, { method: 'DELETE' })
    const data = await response.json().catch(() => ({}))
    if (!response.ok) throw new Error(data.detail || 'No pude eliminar el avatar.')
    const profile = profileWithAvatarUrl(data.profile)
    setProfiles((current) => current.map((item) => item.id === profileId ? profile : item))
    if (activeProfile?.id === profileId) setActiveProfile(profile)
    return profile
  }

  const deleteProfile = async (profileId) => {
    const response = await fetch(`${API_BASE_URL}/profiles/${profileId}`, { method: 'DELETE' })
    if (!response.ok) throw new Error('Profile deletion failed')
    const data = await response.json()
    setProfiles((current) => current.filter((profile) => profile.id !== profileId))
    localStorage.removeItem(conversationStorageKey(profileId))

    if (activeProfile?.id === profileId) {
      localStorage.removeItem(ACTIVE_PROFILE_KEY)
      setActiveProfile(null)
      setConversationId(null)
      setMessages([])
      setHistoryItems([])
      setQuestion('')
      setVideoTopic(null)
      setShowProfileScreen(true)
    }

    return data.deleted_profile
  }

  const resetLocalProfile = () => {
    localStorage.removeItem(ACTIVE_PROFILE_KEY)
    setActiveProfile(null)
    setConversationId(null)
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
        conversation_id: conversationId,
      }),
    })
    if (!response.ok) throw new Error('Demo tutor request failed')
    return response.json()
  }

  const testAiLocal = async () => {
    setIsAiTesting(true)
    setAiTestMessage('')
    try {
      const response = await fetch(`${API_BASE_URL}/ai/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: 'Explica qué es una fracción para quinto básico en una frase.' }),
      })
      const data = await response.json()
      setAiTestMessage(data.status === 'ok' ? 'IA local respondió correctamente.' : (data.message || 'IA local no disponible.'))
      await loadAiStatus()
    } catch {
      setAiTestMessage('No pude conectar con la IA local.')
    } finally {
      setIsAiTesting(false)
    }
  }

  const sendQuestion = async () => {
    const cleanQuestion = question.trim()
    if (!cleanQuestion || isSending) return
    setQuestion('')
    setVideoTopic(detectVideoTopic(cleanQuestion))
    setIsSending(true)
    setMessages((current) => [...current, { from: 'student', text: cleanQuestion }])
    try {
      const data = await fetchDemoAnswer(cleanQuestion)
      setMessages((current) => [
        ...current,
        {
          from: 'assistant',
          text: data.answer,
          nexoVariant: pickNexoVariantForSubject(subject),
          summary: data.summary,
          processingTimeMs: data.processing_time_ms,
          usedLocalContent: data.used_local_content,
          contentSources: data.content_sources ?? [],
          relatedSources: data.related_sources ?? [],
          provenanceStatus: data.provenance_status ?? 'demo_fallback',
          effectiveCourse: data.effective_course,
          sourceCourse: data.source_course,
          foundInOtherCourse: data.found_in_other_course,
          conversationContext: data.conversation_context,
        },
      ])
      setBackendStatus(data.status === 'ok' ? 'connected' : 'unavailable')
      await loadHistory()
    } catch {
      setMessages((current) => [...current, {
        from: 'assistant',
        text: 'No pude generar la respuesta en este momento. Puedes intentar nuevamente.',
        nexoVariant: pickNexoVariantForSubject(subject),
      }])
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
      { from: 'assistant', text: `${responsePrefix(activeProfile)}\n\n${detail}`, nexoVariant: pickNexoVariantForSubject(subject) },
    ])
  }

  const updateHistoryStatus = async (item) => {
    const nextStatus = item.status === 'pendiente' ? 'leido' : 'pendiente'
    try {
      const response = await fetch(`${API_BASE_URL}/history/${item.id}/status`, {
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

  const toggleHistoryFavorite = async (item) => {
    try {
      const response = await fetch(`${API_BASE_URL}/history/${item.id}/favorite`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_favorite: !item.is_favorite }),
      })
      if (!response.ok) throw new Error('Favorite update failed')
      await loadHistory()
    } catch {
      setHistoryError('No pude actualizar el favorito')
    }
  }

  const studyHistoryItem = (item) => {
    setCourse(item.course)
    setMode(item.mode)
    setSubject(item.subject)
    setQuestion(item.question)
    setVideoTopic(detectVideoTopic(item.question))
    setMessages((current) => [
      ...current,
      {
        from: 'assistant',
        text: `Retomemos este tema, ${activeProfile.name}. Dejé la pregunta lista para enviarla nuevamente.`,
        nexoVariant: pickNexoVariantForSubject(item.subject || subject),
      },
    ])
    window.setTimeout(() => document.getElementById('question')?.focus(), 0)
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
      setVideoTopic(detectVideoTopic(data.item.question))
      setMessages((current) => [
        ...current,
        { from: 'student', text: data.item.question },
        {
          from: 'assistant',
          text: data.item.answer_full,
          summary: data.item.answer_summary,
          nexoVariant: pickNexoVariantForSubject(data.item.subject || subject),
        },
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
        onDelete={deleteProfile}
        onAvatarUpload={updateProfileAvatar}
        onAvatarDelete={deleteProfileAvatar}
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
          <h1>{APP_INFO.name}</h1>
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
        <NexoAvatar variant={getNexoVariant({ subject, isIdle: !isSending })} size="welcome" />
        <div>
          <strong>Nexo</strong>
          <p>¡Hola, {activeProfile.name}! Estoy lista para acompañarte.</p>
        </div>
      </section>

      <section className="workspace">
        <aside className="selectors" aria-label="Configuración del estudio">
          <SelectionGroup title="Curso" options={studyCourses} selected={course} onSelect={setCourse} />
          <SelectionGroup title="Modo" options={modes} selected={mode} onSelect={setMode} />
          <SelectionGroup title="Materia" options={subjects} selected={subject} onSelect={setSubject} />
        </aside>

        <section className="chat-panel" aria-label="Chat simulado">
          <header className="chat-header">
            <div>
              <span>{course}</span>
              <strong>{subject}</strong>
              {courseStatusMessage && <small className="active-course-note">{courseStatusMessage}</small>}
            </div>
            <p>{mode}</p>
          </header>
          <div className="messages">
            {messages.map((message, index) => (message.from === 'student' ? (
              <UserMessageBubble key={`${message.from}-${index}`} message={message} profile={activeProfile} />
            ) : (
              <AssistantMessageBubble key={`${message.from}-${index}`} message={message} subject={subject}>
                <SourceNotice message={message} />
                {message.conversationContext?.used_context && (
                  <small className="conversation-context-note">
                    Continuamos el tema: {message.conversationContext.active_topic}.
                  </small>
                )}
                {message.summary && <small className="message-summary">Resumen: {message.summary}</small>}
                {formatProcessingTime(message.processingTimeMs) && (
                  <small className="processing-time">{formatProcessingTime(message.processingTimeMs)}</small>
                )}
              </AssistantMessageBubble>
            )))}
            {isSending && <ProcessingIndicator message={processingMessage} />}
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
              <button type="submit" disabled={isSending} aria-busy={isSending}>
                {isSending ? 'Procesando...' : 'Enviar'}
              </button>
            </div>
          </form>
        </section>

        <aside className="side-panel">
          <AiLocalCard
            status={aiStatus}
            onTest={testAiLocal}
            isTesting={isAiTesting}
            testMessage={aiTestMessage}
          />
          <section className="history-card" aria-label="Historial simple">
            <div className="section-title">
              <div>
                <h2>{historyTitleFor(activeProfile.role)}</h2>
                <small>Historial de {activeProfile.name}</small>
              </div>
            </div>
            {latestHistory ? (
              <div className="latest-question">
                <span>Última pregunta</span>
                <strong>{latestHistory.question}</strong>
              </div>
            ) : (
              <p className="empty-history">Aún no hay preguntas guardadas para este perfil.</p>
            )}
            {latestHistory && (
              <>
                <div className="history-tabs" aria-label="Filtros de historial">
                  <button className={historyView === 'recent' ? 'active' : ''} type="button" onClick={() => setHistoryView('recent')}>
                    Últimas 5
                  </button>
                  <button className={historyView === 'pending' ? 'active' : ''} type="button" onClick={() => setHistoryView('pending')}>
                    Pendientes <span>{pendingHistory.length}</span>
                  </button>
                  <button className={historyView === 'favorites' ? 'active' : ''} type="button" onClick={() => setHistoryView('favorites')}>
                    Favoritas <span>{favoriteHistory.length}</span>
                  </button>
                </div>
                <div className="history-list">
                  {visibleHistoryItems.length > 0 ? visibleHistoryItems.map((item) => (
                    <article className="history-item" key={item.id}>
                      <div className="history-item-heading">
                        <strong>{item.question}</strong>
                        {item.is_favorite && <span className="favorite-mark" title="Favorita">★</span>}
                      </div>
                      <p>{item.answer_summary || 'Sin resumen disponible.'}</p>
                      <div className="history-meta">
                        <span>{item.course}</span>
                        <span>{item.subject || 'Sin materia'}</span>
                        <span>{item.mode}</span>
                        <span>{formatHistoryDate(item.created_at)}</span>
                      </div>
                      <span className={`status ${item.status}`}>{item.status}</span>
                      <div className="history-item-actions">
                        <button type="button" onClick={() => updateHistoryStatus(item)}>
                          Marcar {item.status === 'pendiente' ? 'leído' : 'pendiente'}
                        </button>
                        <button type="button" onClick={() => toggleHistoryFavorite(item)}>
                          {item.is_favorite ? 'Quitar favorito' : 'Favorito'}
                        </button>
                        <button className="study-again" type="button" onClick={() => studyHistoryItem(item)}>
                          Volver a estudiar
                        </button>
                      </div>
                    </article>
                  )) : (
                    <p className="empty-history-list">
                      {historyView === 'pending' ? 'No hay preguntas pendientes.' : 'No hay preguntas favoritas.'}
                    </p>
                  )}
                </div>
              </>
            )}
            {historyError && <p className="history-error">{historyError}</p>}
            <button className="continue-button" type="button" disabled={!latestHistory} onClick={continueLatestHistory}>Continuar donde quedé</button>
          </section>

          <section className="videos" aria-label="Videos recomendados">
            <h2>{videoTopic && topicVideos.length > 0 ? `Videos sobre ${videoTopic}` : 'Videos recomendados'}</h2>
            {recommendedVideos.length > 0 ? (
              <div className="video-list">
                {recommendedVideos.map((video) => (
                  <article className="video-card" key={video.id}>
                    <div className="video-thumb" aria-hidden="true">▶</div>
                    <div className="video-card-content">
                      <h3>{video.title}</h3>
                      <p><strong>Tema:</strong> {video.topic}</p>
                      <p>{video.channel}</p>
                      <small>{video.duration}</small>
                      <span className={`review-status ${video.reviewed ? 'reviewed' : 'pending'}`}>
                        {video.reviewed ? 'Revisado' : 'Pendiente de revisión'}
                      </span>
                      <a href={video.url} target="_blank" rel="noreferrer">Abrir video</a>
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <p className="empty-videos">
                {videoLoadError ? 'No pude cargar los videos disponibles.' : 'No hay videos disponibles.'}
              </p>
            )}
            <p className="video-safety-note">Este material es un apoyo educativo. Revisa con un adulto los temas sensibles.</p>
          </section>
        </aside>
      </section>
      <footer className="app-footer">
        <p>
          {APP_INFO.name} · Desarrollado por {APP_INFO.author} · © {APP_INFO.year}
        </p>
        <button type="button" onClick={() => setIsAboutOpen(true)}>Acerca de</button>
      </footer>
      {isAboutOpen && <AboutPanel onClose={() => setIsAboutOpen(false)} />}
    </main>
  )
}

export default App
