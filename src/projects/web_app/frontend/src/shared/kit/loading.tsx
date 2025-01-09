import React, { useEffect, useState } from 'react'

import { cn } from '../lib'
import { Progress } from '../ui'

export const Loading = ({
  message,
  type,
}: {
  message: React.ReactNode
  type: 'container' | 'page'
}) => {
  const [progress, setProgress] = useState(13)

  useEffect(() => {
    const timer = setTimeout(() => setProgress(66), 200)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div
      className={cn(
        'w-full flex items-center justify-center',
        type === 'page' ? 'h-screen text-text bg-background' : 'pt-10'
      )}
    >
      <div className="mx-auto w-full text-center md:max-w-xs px-8 space-y-4">
        {message}
        <Progress value={progress} />
      </div>
    </div>
  )
}
