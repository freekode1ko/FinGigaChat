import { useState } from 'react'
import { toast } from 'sonner'

import { useDeleteMessageMutation } from '@/entities/bot'
import { AdaptableModal } from '@/shared/kit'
import { Button, Paragraph } from '@/shared/ui'

const DeleteMessageDialog = ({
  broadcastId,
  children,
}: {
  broadcastId: number
  children: React.ReactNode
}) => {
  const [delete_] = useDeleteMessageMutation()
  const [open, setOpen] = useState(false)
  const handleDelete = () => {
    toast.promise(delete_({ broadcastId }).unwrap(), {
      loading: `Удаляем рассылку...`,
      success: () => {
        setOpen(false)
        return 'Рассылка успешно удалена!'
      },
      error: 'Мы не смогли удалить рассылку. Попробуйте позже.',
    })
  }

  return (
    <AdaptableModal
      open={open}
      onOpenChange={setOpen}
      title='Удалить рассылку'
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
        Вы уверены, что хотите удалить рассылку? Это действие будет невозможно отменить, а сообщение удалится у всех пользователей, которые его получили.
      </Paragraph>
    </AdaptableModal>
  )
}

export { DeleteMessageDialog }
