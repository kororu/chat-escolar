import { useEffect, useState } from 'react'
import './App.css'

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
  const [lastQuestion, setLastQuestion] = useState('¿Qué es un hábitat?')
  const [status, setStatus] = useState('pendiente')
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

  useEffect(() => {
    const controller = new AbortController()

    const checkBackend = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/health', {
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

  const sendQuestion = () => {
    const cleanQuestion = question.trim()

    if (!cleanQuestion) {
      return
    }

    setMessages((currentMessages) => [
      ...currentMessages,
      { from: 'student', text: cleanQuestion },
      {
        from: 'assistant',
        text:
          'Buena pregunta. La vamos a trabajar con calma.\n\nExplicación corta:\nPrimero miramos la idea principal.\n\nEjemplo:\nSi el tema parece difícil, lo dividimos en partes pequeñas.\n\nMini resumen:\nAprender paso a paso ayuda a entender mejor.\n\nPregunta:\n¿Qué parte quieres revisar primero?',
      },
    ])
    setLastQuestion(cleanQuestion)
    setStatus('pendiente')
    setQuestion('')
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
    setLastQuestion(action)
    setStatus('pendiente')
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
              <button type="submit">Enviar</button>
            </div>
          </form>
        </section>

        <aside className="side-panel">
          <section className="history-card" aria-label="Historial simple">
            <div className="section-title">
              <h2>Historial</h2>
              <button
                type="button"
                onClick={() => setStatus(status === 'pendiente' ? 'leído' : 'pendiente')}
              >
                Marcar {status === 'pendiente' ? 'leído' : 'pendiente'}
              </button>
            </div>
            <dl>
              <div>
                <dt>Última pregunta</dt>
                <dd>{lastQuestion}</dd>
              </div>
              <div>
                <dt>Estado</dt>
                <dd>
                  <span className={`status ${status}`}>{status}</span>
                </dd>
              </div>
            </dl>
            <button className="continue-button" type="button">
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
