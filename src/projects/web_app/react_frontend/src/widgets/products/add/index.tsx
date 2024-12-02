import { CreateProductForm } from '@/features/products/add'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/shared/ui'

interface CreateProductDialogProps {
  open: boolean
  onOpenChange: (value: boolean) => void
}

const CreateProductDialog = ({
  open,
  onOpenChange,
}: CreateProductDialogProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Создать новый продукт</DialogTitle>
        </DialogHeader>
        <CreateProductForm
          onSuccess={() => {
            onOpenChange(false)
          }}
        />
      </DialogContent>
    </Dialog>
  )
}

export { CreateProductDialog }
