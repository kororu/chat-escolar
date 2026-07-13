import nexoReposo from './nexo_reposo.png'
import nexoRespuesta from './nexo_respuesta.png'
import nexoPensando from './nexo_pensando.png'
import nexoPregunta from './nexo_pregunta.png'
import nexoFelicitacion from './nexo_felicitacion.png'
import nexoBienvenida from './nexo_bienvenida.png'
import nexoMatematica01 from './nexo_matematica_01.png'
import nexoMatematica02 from './nexo_matematica_02.png'
import nexoCiencias01 from './nexo_ciencias_01.png'
import nexoCiencias02 from './nexo_ciencias_02.png'
import nexoHistoria01 from './nexo_historia_01.png'
import nexoHistoria02 from './nexo_historia_02.png'
import nexoLenguaje01 from './nexo_lenguaje_01.png'
import nexoLenguaje02 from './nexo_lenguaje_02.png'

export const NEXO_VARIANTS = {
  reposo: nexoReposo,
  respuesta: nexoRespuesta,
  pensando: nexoPensando,
  pregunta: nexoPregunta,
  felicitacion: nexoFelicitacion,
  bienvenida: nexoBienvenida,
  matematica_01: nexoMatematica01,
  matematica_02: nexoMatematica02,
  ciencias_01: nexoCiencias01,
  ciencias_02: nexoCiencias02,
  historia_01: nexoHistoria01,
  historia_02: nexoHistoria02,
  lenguaje_01: nexoLenguaje01,
  lenguaje_02: nexoLenguaje02,
}

export const NEXO_SUBJECT_VARIANTS = {
  matematica: ['matematica_01', 'matematica_02'],
  ciencias: ['ciencias_01', 'ciencias_02'],
  historia: ['historia_01', 'historia_02'],
  lenguaje: ['lenguaje_01', 'lenguaje_02'],
}

function normalizeSubject(subject = '') {
  return subject
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
}

export function getNexoSubjectKey(subject) {
  const normalized = normalizeSubject(subject)
  if (normalized.includes('matematica')) return 'matematica'
  if (normalized.includes('ciencias')) return 'ciencias'
  if (normalized.includes('historia')) return 'historia'
  if (/(lenguaje|comunicacion|lectura|escritura)/.test(normalized)) return 'lenguaje'
  return null
}

export function pickNexoVariantForSubject(subject, random = Math.random) {
  const subjectKey = getNexoSubjectKey(subject)
  const options = subjectKey ? NEXO_SUBJECT_VARIANTS[subjectKey] : null
  if (!options?.length) return 'respuesta'
  return options[Math.floor(random() * options.length)]
}

export function getNexoVariant({
  isProcessing = false,
  isCongratulations = false,
  isQuestion = false,
  subject = '',
  messageNexoVariant,
  isIdle = false,
} = {}) {
  if (isProcessing) return 'pensando'
  if (isCongratulations) return 'felicitacion'
  if (isQuestion) return 'pregunta'
  if (messageNexoVariant) return messageNexoVariant
  const subjectKey = getNexoSubjectKey(subject)
  if (subjectKey) return NEXO_SUBJECT_VARIANTS[subjectKey][0]
  if (isIdle) return 'reposo'
  return 'respuesta'
}

export function resolveNexoAsset(variant) {
  return NEXO_VARIANTS[variant] ?? NEXO_VARIANTS.respuesta
}
