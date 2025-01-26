import { toast } from "sonner"

import { useDeleteIndustryDocumentMutation } from "@/entities/industries"
import { DeleteConfirmationButton } from "@/shared/kit"

const DeleteIndustryDocumentButton = ({ id }: { id: number }) => {
  const [deleteDocument, { isLoading }] = useDeleteIndustryDocumentMutation()
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

export { DeleteIndustryDocumentButton }
