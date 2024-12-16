import { X } from 'lucide-react'
import { toast } from 'sonner'

import { useDeleteWhitelistMutation } from '@/entities/whitelist'
import {
  Button,
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  Paragraph,
} from '@/shared/ui'

interface DeleteFromWhitelistProps {
  email: string
}

const DeleteFromWhitelistDialog = ({ email }: DeleteFromWhitelistProps) => {
  const [deleteFromWhitelist] = useDeleteWhitelistMutation()
  const handleDelete = () => {
    toast.promise(deleteFromWhitelist({ email }).unwrap(), {
      loading: `Удаляем ${email} из белого списка...`,
      success: 'Пользователь успешно удален!',
      error: 'Мы не смогли удалить пользователя. Попробуйте позже.',
    })
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon">
          <X />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Удалить {email}</DialogTitle>
        </DialogHeader>
        <Paragraph>
          Вы уверены, что хотите удалить этого пользователя из белого списка?
          Действие будет невозможно отменить.
        </Paragraph>
        <DialogFooter>
          <DialogClose asChild>
            <Button type="button" variant="outline">
              Отмена
            </Button>
          </DialogClose>
          <DialogClose asChild>
            <Button type="submit" variant="destructive" onClick={handleDelete}>
              Удалить
            </Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export { DeleteFromWhitelistDialog }
