import { useState } from 'react'
import { toast } from 'sonner'

import { useDeleteWhitelistMutation } from '@/entities/whitelist'
import { AdaptableModal } from '@/shared/kit'
import { Button, Paragraph } from '@/shared/ui'

interface DeleteFromWhitelistProps extends React.PropsWithChildren {
  email: string
}

const DeleteFromWhitelistDialog = ({
  email,
  children,
}: DeleteFromWhitelistProps) => {
  const [delete_] = useDeleteWhitelistMutation()
  const [open, setOpen] = useState(false)
  const handleDelete = () => {
    toast.promise(delete_({ email }).unwrap(), {
      loading: `Удаляем ${email} из белого списка...`,
      success: () => {
        setOpen(false)
        return 'E-Mail успешно удален из белого списка!'
      },
      error: 'Мы не смогли удалить пользователя. Попробуйте позже.',
    })
  }

  return (
    <AdaptableModal
      open={open}
      onOpenChange={setOpen}
      title={`Удалить ${email}`}
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
        Вы уверены, что хотите удалить этого пользователя из белого списка?
        Действие будет невозможно отменить.
      </Paragraph>
    </AdaptableModal>
  )
}

export { DeleteFromWhitelistDialog }
