import { toast } from "sonner"

import { useDeleteProductDocumentMutation } from "@/entities/products"
import { DeleteConfirmationButton } from "@/shared/kit"

const DeleteProductDocumentButton = ({ id }: { id: number }) => {
  const [deleteDocument, { isLoading }] = useDeleteProductDocumentMutation()
  const handleDelete = () => {  
    toast.promise(
      deleteDocument({ id }).unwrap(),
      {
        loading: `Удаляем документ...`,
        success: 'Документ успешно удален!',
        error: 'Мы не смогли удалить документ. Попробуйте позже.',
      }
    )
  }

  return (
    <DeleteConfirmationButton onConfirm={handleDelete} disabled={isLoading} />
  )
}

export { DeleteProductDocumentButton }
