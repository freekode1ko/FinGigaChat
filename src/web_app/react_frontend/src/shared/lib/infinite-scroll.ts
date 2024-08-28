import React from 'react'

const useInfiniteScroll = () => {
  const [page, setPage] = React.useState<number>(1)
  const observer = React.useRef<Optional<IntersectionObserver>>(null)
  const triggerRef = React.useCallback((node: HTMLDivElement) => {
    if (observer.current) observer.current.disconnect()
    observer.current = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        setPage((prevPage) => prevPage + 1)
      }
    })
    if (node) observer.current.observe(node)
  }, [])

  return {
    page,
    setPage,
    triggerRef,
  }
}

export { useInfiniteScroll }
