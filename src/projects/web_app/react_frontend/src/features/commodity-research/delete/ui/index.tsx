import { toast } from "sonner"

import { useDeleteCommodityResearchMutation } from "@/entities/commodity"
import { DeleteConfirmationButton } from "@/shared/kit"

const DeleteCommodityResearchButton = ({ id }: { id: number }) => {
  const [deleteResearch, { isLoading }] = useDeleteCommodityResearchMutation()
  const handleDelete = () => {  
    toast.promise(
      deleteResearch({ id }).unwrap(),
      {
        loading: `Удаляем аналитику...`,
        success: 'Аналитика успешно удалена!',
        error: 'Мы не смогли удалить аналитику. Попробуйте позже.',
      }
    )
  }

  return (
    <DeleteConfirmationButton onConfirm={handleDelete} disabled={isLoading} />
  )
}

export { DeleteCommodityResearchButton }
