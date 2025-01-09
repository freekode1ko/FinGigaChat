import { useState } from 'react'

import type { User } from '@/entities/user'
import { AdaptableModal } from '@/shared/kit'

import { UpdateUserRoleForm } from './form'

const UpdateUserRoleDialog = ({
  user,
  children,
}: {
  user: User
  children: React.ReactNode
}) => {
  const [open, setOpen] = useState(false)
  return (
    <AdaptableModal
      open={open}
      onOpenChange={setOpen}
      title={`Изменить роль ${user.email}`}
      trigger={children}
    >
      <UpdateUserRoleForm user={user} onSuccess={() => setOpen(false)} />
    </AdaptableModal>
  )
}

export { UpdateUserRoleDialog }
