import { useState } from 'react'

import {
  Button,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/shared/ui'

import { CreateWhitelistForm } from './form'

const CreateWhitelistDialog = () => {
  const [openDialog, setOpenDialog] = useState(false)

  return (
    <Dialog open={openDialog} onOpenChange={setOpenDialog}>
      <DialogTrigger asChild>
        <Button>Добавить пользователя</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Добавить пользователя</DialogTitle>
          <DialogDescription>
            Пользователь сможет зарегистрироваться в Telegram боте
          </DialogDescription>
        </DialogHeader>
        <CreateWhitelistForm onSuccess={() => setOpenDialog(false)} />
      </DialogContent>
    </Dialog>
  )
}

export { CreateWhitelistDialog }
