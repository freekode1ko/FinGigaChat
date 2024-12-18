import { useState } from 'react'

import { AdaptableModal } from '@/shared/kit'

import { CreateWhitelistForm } from './form'

const CreateWhitelistDialog = ({ children }: { children: React.ReactNode }) => {
  const [open, setOpen] = useState(false)
  return (
    <AdaptableModal
      open={open}
      onOpenChange={setOpen}
      title="Добавить пользователя"
      trigger={children}
    >
      <CreateWhitelistForm onSuccess={() => setOpen(false)} />
    </AdaptableModal>
  )
}

export { CreateWhitelistDialog }
