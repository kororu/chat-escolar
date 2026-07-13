function initialFor(name) {
  const firstCharacter = Array.from((name || '').trim())[0]
  return (firstCharacter || 'U').toLocaleUpperCase('es-CL')
}

export function UserAvatar({ name, imageUrl, color }) {
  return (
    <div
      className="user-avatar"
      aria-label={`Avatar de ${name || 'usuario'}`}
      role="img"
      style={color ? { '--user-avatar-color': color } : undefined}
    >
      {imageUrl ? <img alt="" src={imageUrl} /> : <span aria-hidden="true">{initialFor(name)}</span>}
    </div>
  )
}
