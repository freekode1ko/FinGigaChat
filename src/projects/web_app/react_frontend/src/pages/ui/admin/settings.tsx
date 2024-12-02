import { useState } from 'react'
import { toast } from 'sonner'

import {
  type Setting,
  useGetSettingsQuery,
  useSetSettingMutation,
} from '@/entities/settings'
import {
  Button,
  Popover,
  PopoverContent,
  PopoverTrigger,
  Textarea,
  TypographyH2,
} from '@/shared/ui'

const AdminSettingsPage = () => {
  const { data: settings } = useGetSettingsQuery()
  if (!settings) return <div>loading...</div>

  return (
    <div className="p-4">
      <div className="mb-2">
        <TypographyH2>Настройки приложения</TypographyH2>
      </div>
      <div className="py-4 flex flex-row gap-4">
        {settings.map((setting) => (
          <SettingEdit key={setting.key} setting={setting} />
        ))}
      </div>
    </div>
  )
}

const SettingEdit = ({ setting }: { setting: Setting }) => {
  const [trigger] = useSetSettingMutation()
  const [newValue, setNewValue] = useState(setting.value)
  const handleSave = () => {
    toast.promise(trigger({ key: setting.key, newValue }).unwrap(), {
      loading: 'Сохраняем изменения...',
      success: 'Изменения сохранены!',
      error: 'Мы не смогли сохранить изменения. Попробуйте позже.',
    })
  }

  return (
    <Popover
      onOpenChange={(open) => {
        if (!open && newValue !== setting.value) handleSave()
      }}
    >
      <PopoverTrigger asChild>
        <Button variant="outline">{setting.name}</Button>
      </PopoverTrigger>
      <PopoverContent className="relative text-text w-80">
        <div className="space-y-2">
          <h4 className="font-medium leading-none">{setting.name}</h4>
          <p className="text-sm text-muted-foreground">{setting.key}</p>
          <Textarea
            value={newValue}
            onChange={(e) => setNewValue(e.target.value)}
          />
        </div>
      </PopoverContent>
    </Popover>
  )
}

export { AdminSettingsPage }
