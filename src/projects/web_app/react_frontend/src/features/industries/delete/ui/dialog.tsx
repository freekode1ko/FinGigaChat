import { useState } from 'react'
import { toast } from 'sonner'

import { type Industry, useDeleteIndustryMutation } from '@/entities/industries'
import { AdaptableModal } from '@/shared/kit'
import { Button, Paragraph } from '@/shared/ui'

const DeleteIndustryDialog = ({
  industry,
  children,
}: {
  industry: Industry
  children: React.ReactNode
}) => {
  const [delete_] = useDeleteIndustryMutation()
  const [open, setOpen] = useState(false)
  const handleDelete = () => {
    toast.promise(delete_({ id: industry.id }).unwrap(), {
      loading: `Удаляем ${industry.name}...`,
      success: () => {
        setOpen(false)
        return 'Отрасль успешно удалена!'
      },
      error: 'Мы не смогли удалить отрасль. Попробуйте позже.',
    })
  }

  return (
    <AdaptableModal
      open={open}
      onOpenChange={setOpen}
      title={`Удалить ${industry.name}`}
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
        Вы уверены, что хотите удалить эту отрасль? Действие будет невозможно
        отменить.
      </Paragraph>
    </AdaptableModal>
  )
}

export { DeleteIndustryDialog }
