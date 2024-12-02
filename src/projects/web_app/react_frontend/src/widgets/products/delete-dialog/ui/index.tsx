import { toast } from 'sonner'

import { type Product, useDeleteProductMutation } from '@/entities/products'
import {
  Button,
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui'

interface DeleteProductDialogProps {
  item: Product
  open: boolean
  onOpenChange: (value: boolean) => void
}

const DeleteProductDialog = ({
  item,
  open,
  onOpenChange,
}: DeleteProductDialogProps) => {
  const [trigger] = useDeleteProductMutation()
  const handleDeleteProduct = () => {
    toast.promise(trigger({ id: item.id }).unwrap(), {
      loading: 'Удаляем продукт...',
      success: 'Продукт успешно удален!',
      error: 'Мы не смогли удалить продукт. Попробуйте позже.',
    })
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Удалить {item.name}</DialogTitle>
        </DialogHeader>
        <p>Вы уверены, что хотите удалить этот продукт?</p>
        <DialogFooter>
          <Button
            type="submit"
            variant="destructive"
            onClick={handleDeleteProduct}
          >
            Подтвердить
          </Button>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Отменить
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export { DeleteProductDialog }
