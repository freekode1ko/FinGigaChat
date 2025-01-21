import { SendMessageDialog } from "@/features/bot/send-message"
import { Button } from "@/shared/ui"


export function AdminBotPage() {
  return (
    <div className="container mx-auto p-6">
      <h1 className="text-2xl font-bold">Управление ботом</h1>
      <div className="space-y-4 mt-6">
        <div className="flex flex-row gap-4">
          <SendMessageDialog>
            <Button>Создать рассылку</Button>
          </SendMessageDialog>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          Content
        </div>
      </div>
    </div>
  )
}

// const ManageBroadcastDropdown = () => {
//   return (
//     <DropdownMenu modal={false}>
//       <DropdownMenuTrigger asChild>
//         <Button size="icon" variant="ghost">
//           <EllipsisVertical className="h-6 w-6" />
//         </Button>
//       </DropdownMenuTrigger>
//       <DropdownMenuContent className="w-56">
//         <DropdownMenuLabel>Управление рассылкой</DropdownMenuLabel>
//         <DropdownMenuSeparator />
//         <DropdownMenuGroup>
//           <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
//             Редактировать
//           </DropdownMenuItem>
//           <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
//             Удалить
//           </DropdownMenuItem>
//         </DropdownMenuGroup>
//       </DropdownMenuContent>
//     </DropdownMenu>
//   )
// }
