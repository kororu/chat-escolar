import { getNexoVariant } from '../assets/nexo/nexoVariants'
import { NexoAvatar } from './NexoAvatar'
import { UserAvatar } from './UserAvatar'

export function UserMessageBubble({ message, profile }) {
  return (
    <article className="chat-message-row user-message-row">
      <div className="chat-bubble user-bubble">
        <span>{profile?.name || 'Usuario'}</span>
        <p>{message.text}</p>
      </div>
      <UserAvatar
        name={profile?.name}
        imageUrl={profile?.avatarUrl || profile?.avatarImage}
        color={profile?.avatarColor}
      />
    </article>
  )
}

export function AssistantMessageBubble({ message, subject, children }) {
  const variant = getNexoVariant({
    subject,
    messageNexoVariant: message.nexoVariant,
    isCongratulations: message.nexoState === 'felicitacion',
    isQuestion: message.nexoState === 'pregunta',
  })
  return (
    <article className="chat-message-row assistant-bubble-row">
      <NexoAvatar variant={variant} size="small" />
      <div className="chat-bubble assistant-bubble">
        <span>Nexo</span>
        <p>{message.text}</p>
        {children}
      </div>
    </article>
  )
}
