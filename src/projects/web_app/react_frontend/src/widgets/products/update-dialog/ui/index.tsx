import { CreateProductForm } from '@/features/products/add'
import type { Product } from '@/entities/products'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/shared/ui'

interface UpdateProductDialogProps {
  item: Product
  open: boolean
  onOpenChange: (value: boolean) => void
}

const UpdateProductDialog = ({
  item,
  open,
  onOpenChange,
}: UpdateProductDialogProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Редактировать {item.name}</DialogTitle>
        </DialogHeader>
        <CreateProductForm
          item={item}
          onSuccess={() => {
            onOpenChange(false)
          }}
        />
      </DialogContent>
    </Dialog>
  )
}

export { UpdateProductDialog }
