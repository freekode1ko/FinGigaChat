import { Check, X } from "lucide-react"
import { useEffect, useState } from "react"

import { Button } from "@/shared/ui/button"

const DeleteConfirmationButton = ({ onConfirm, disabled }: { onConfirm: () => void, disabled: boolean }) => {
  const [confirm, setConfirm] = useState(false)
  useEffect(() => {
    if (confirm) {
      setTimeout(() => setConfirm(false), 3000)
    }
  }, [confirm])

  return (
    <div className="flex items-center gap-2">
      {confirm ? 
        <Button onClick={onConfirm} disabled={disabled} variant='ghost' className="bg-secondary"><span>Точно удалить?</span><Check className="w-4 h-4" /></Button> : 
        <Button onClick={() => setConfirm(true)} size='icon' variant='ghost'><X className="w-4 h-4" /></Button>
      }
    </div>
  )
}

export { DeleteConfirmationButton }
