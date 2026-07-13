import { useEffect, useState } from 'react'
import { resolveNexoAsset } from '../assets/nexo/nexoVariants'

export function NexoAvatar({ variant = 'reposo', size = 'regular' }) {
  const [imageUnavailable, setImageUnavailable] = useState(false)

  useEffect(() => setImageUnavailable(false), [variant])

  return (
    <div className={`nexo-avatar nexo-${size} nexo-${variant}`} aria-label={`Nexo: ${variant}`} role="img">
      {!imageUnavailable && (
        <img
          alt=""
          src={resolveNexoAsset(variant)}
          onError={() => setImageUnavailable(true)}
        />
      )}
      {imageUnavailable && <span aria-hidden="true">N</span>}
    </div>
  )
}
