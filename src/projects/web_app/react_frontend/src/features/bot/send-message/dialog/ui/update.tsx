import { useState } from 'react'

import type { FullBroadcast } from '@/entities/bot'
import { AdaptableModal } from '@/shared/kit'

import { UpdateMessageForm } from '../../form/ui/update'

const UpdateMessageDialog = ({
  children,
  broadcast,
}: {
  children: React.ReactNode
  broadcast: FullBroadcast
}) => {
  const [open, setOpen] = useState(false)
  return (
    <AdaptableModal
      open={open}
      onOpenChange={setOpen}
      title="Редактировать рассылку"
      trigger={children}
    >
      <UpdateMessageForm broadcast={broadcast} onSuccess={() => setOpen(false)} />
    </AdaptableModal>
  )
}

export { UpdateMessageDialog }
