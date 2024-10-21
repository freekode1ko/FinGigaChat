import { useEffect, useState } from 'react'

/* value and delay in ms (1000ms = 1s) */
const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const t = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)
    return () => {
      clearTimeout(t)
    }
  }, [value, delay])
  return debouncedValue
}

export { useDebounce }
