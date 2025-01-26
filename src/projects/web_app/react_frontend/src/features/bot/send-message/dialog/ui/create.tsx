import { useState } from 'react'

import { SendMessageForm } from '@/features/bot/send-message/form'
import { AdaptableModal } from '@/shared/kit'

const SendMessageDialog = ({ children }: { children: React.ReactNode }) => {
  const [open, setOpen] = useState(false)
  return (
    <AdaptableModal
      open={open}
      onOpenChange={setOpen}
      title="Создать рассылку"
      trigger={children}
    >
      <SendMessageForm onSuccess={() => setOpen(false)} />
    </AdaptableModal>
  )
}

export { SendMessageDialog }
