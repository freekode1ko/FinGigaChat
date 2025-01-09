import { useState } from 'react'
import { toast } from 'sonner'

import { type Product, useDeleteProductMutation } from '@/entities/products'
import { AdaptableModal } from '@/shared/kit'
import { Button, Paragraph } from '@/shared/ui'

const DeleteProductDialog = ({
  product,
  children,
}: {
  product: Product
  children: React.ReactNode
}) => {
  const [delete_] = useDeleteProductMutation()
  const [open, setOpen] = useState(false)
  const handleDelete = () => {
    toast.promise(delete_({ id: product.id }).unwrap(), {
      loading: `Удаляем ${product.name}...`,
      success: () => {
        setOpen(false)
        return 'Продукт успешно удален!'
      },
      error: 'Мы не смогли удалить продукт. Попробуйте позже.',
    })
  }

  return (
    <AdaptableModal
      open={open}
      onOpenChange={setOpen}
      title={`Удалить ${product.name}`}
      trigger={children}
      bottomSlot={
        <>
          <Button
            className="w-full md:w-auto"
            type="button"
            variant="outline"
            onClick={() => setOpen(false)}
          >
            Отмена
          </Button>
          <Button
            className="w-full md:w-auto"
            type="submit"
            variant="destructive"
            onClick={handleDelete}
          >
            Удалить
          </Button>
        </>
      }
    >
      <Paragraph>
        Вы уверены, что хотите удалить этот продукт? Действие будет невозможно
        отменить.
      </Paragraph>
    </AdaptableModal>
  )
}

export { DeleteProductDialog }
