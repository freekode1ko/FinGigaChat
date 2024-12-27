import { SendMessageForm } from '@/features/bot/send-message'

export function AdminBotPage() {
  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Управление ботом</h1>
      </div>
      <div className="space-y-2">
        <div className="flex flex-col gap-4 p-4">
          <h2 className="text-xl font-bold">Создать рассылку</h2>
          <SendMessageForm />
        </div>
      </div>
    </div>
  )
}
