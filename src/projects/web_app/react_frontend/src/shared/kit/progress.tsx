import { useEffect, useState } from 'react'

import { Progress } from '../ui'

export const AutoProgress = () => {
  const [progress, setProgress] = useState(13)
  useEffect(() => {
    const timer = setTimeout(() => setProgress(66), 500)
    return () => clearTimeout(timer)
  }, [])

  return <Progress value={progress} />
}
