import { useState } from 'react'

import { AdaptableModal } from '@/shared/kit'

import { CreateProductForm } from './form'

const CreateProductDialog = ({ children }: { children: React.ReactNode }) => {
  const [open, setOpen] = useState(false)
  return (
    <AdaptableModal
      open={open}
      onOpenChange={setOpen}
      title="Добавить продукт"
      trigger={children}
    >
      <CreateProductForm onSuccess={() => setOpen(false)} />
    </AdaptableModal>
  )
}

export { CreateProductDialog }
