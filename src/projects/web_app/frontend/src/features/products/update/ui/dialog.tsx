import { useState } from 'react'

import { type Product } from '@/entities/products'
import { AdaptableModal } from '@/shared/kit'

import { UpdateProductForm } from './form'

const UpdateProductDialog = ({
  product,
  children,
}: {
  product: Product
  children: React.ReactNode
}) => {
  const [open, setOpen] = useState(false)
  return (
    <AdaptableModal
      open={open}
      onOpenChange={setOpen}
      title={`Редактировать ${product.name}`}
      trigger={children}
    >
      <UpdateProductForm product={product} onSuccess={() => setOpen(false)} />
    </AdaptableModal>
  )
}

export { UpdateProductDialog }
