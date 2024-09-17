import { useEffect, useRef, useState } from 'react'

const useResizeObserver = (
  initialWidth: number = 400,
  initialHeight: number = 150
) => {
  const [width, setWidth] = useState(initialWidth)
  const [height, setHeight] = useState(initialHeight)
  const containerRef = useRef(null)
  useEffect(() => {
    const resizeObserver = new ResizeObserver((entries) => {
      if (entries[0].contentRect) {
        setWidth(entries[0].contentRect.width)
        setHeight(entries[0].contentRect.height)
      }
    })
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current)
    }
    return () => resizeObserver.disconnect()
  }, [])
  return { containerRef, width, height }
}

export { useResizeObserver }
