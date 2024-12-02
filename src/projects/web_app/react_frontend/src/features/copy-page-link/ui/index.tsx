import { Copy, CopyCheck } from 'lucide-react'
import { useEffect, useState } from 'react'

import { Button } from '@/shared/ui'

const CopyPageLinkButton = () => {
  const [isCopied, setIsCopied] = useState<boolean>(false)
  const handleButtonClick = () => {
    navigator.clipboard.writeText(window.location.href)
    setIsCopied(true)
  }
  useEffect(() => {
    if (isCopied) {
      const timer = setTimeout(() => {
        setIsCopied(false)
      }, 3000)
      return () => clearTimeout(timer)
    }
  }, [isCopied])

  return (
    <Button size="sm" variant="secondary" onClick={handleButtonClick}>
      {isCopied ? (
        <>
          <CopyCheck className="h-4 w-4" /> Скопировано
        </>
      ) : (
        <>
          <Copy className="h-4 w-4" /> Скопировать ссылку
        </>
      )}
    </Button>
  )
}

export { CopyPageLinkButton }
