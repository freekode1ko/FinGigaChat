import { Ellipsis } from "lucide-react"
import { Link, Outlet } from "react-router-dom"

import { DeleteMessageDialog } from "@/features/bot/delete-message"
import { SendMessageDialog, UpdateMessageDialog } from "@/features/bot/send-message"
import { BroadcastCard, type FullBroadcast, useGetMessagesQuery } from "@/entities/bot"
import { ADMIN_MAP } from "@/shared/model"
import { Button, DropdownMenu, DropdownMenuContent, DropdownMenuGroup, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger, Skeleton } from "@/shared/ui"

export const AdminBotPage = () => {
  const { data: broadcast } = useGetMessagesQuery({ page: 1, size: 100})

  return (
    <>
    <div className="container mx-auto p-6">
      <h1 className="text-2xl font-bold">Управление ботом</h1>
      <div className="space-y-4 mt-6">
        <div className="flex flex-row gap-4">
          <SendMessageDialog>
            <Button>Создать рассылку</Button>
          </SendMessageDialog>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {broadcast ? 
            broadcast.messages.map((message) => (
              <BroadcastCard
                key={message.broadcast_id}
                broadcast={message}
                actionSlot={<ManageBroadcastDropdown broadcast={message} />}
                isNewest
              />
            )) :
            Array.from({ length: 9 }).map((_, index) => (
              <Skeleton key={index} className="w-full h-64" />
            ))
          }
        </div>
        {/* {broadcast?.messages && broadcast.messages.length > 9 && <ShowMoreButton ref={triggerRef} />} */}
      </div>
    </div>
    <Outlet />
    </>
  )
}

const ManageBroadcastDropdown = ({broadcast}: {broadcast: FullBroadcast}) => {
  return (
    <DropdownMenu modal={false}>
      <DropdownMenuTrigger asChild>
        <Button size="icon" variant="ghost">
          <Ellipsis className="h-6 w-6" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56">
        <DropdownMenuLabel>Управление рассылкой</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
            <Link to={`${ADMIN_MAP.bot}/${broadcast.broadcast_id}`}>История сообщений</Link>
          </DropdownMenuItem>
        {!broadcast.deleted_at &&
          <>
          <DropdownMenuSeparator />
          <DropdownMenuGroup>
            <UpdateMessageDialog broadcast={broadcast}>
              <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
                Редактировать
              </DropdownMenuItem>
            </UpdateMessageDialog>
            <DeleteMessageDialog broadcastId={broadcast.broadcast_id}>
              <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
                Удалить
              </DropdownMenuItem>
            </DeleteMessageDialog>
          </DropdownMenuGroup>
          </>
        }
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
