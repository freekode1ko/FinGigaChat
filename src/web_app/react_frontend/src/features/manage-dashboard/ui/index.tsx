import { Eye, EyeOff, Grid2X2, List, Settings, Square } from 'lucide-react'
import { useState } from 'react'

import {
  Button,
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  Input,
} from '@/shared/ui'

import { useManageDashboard } from '../lib'

const ManageDashboardButton = () => {
  const {
    handleSave,
    handleCancel,
    handleActiveToggle,
    handleTypeChange,
    searchSubscriptions,
  } = useManageDashboard()

  const [searchQuery, setSearchQuery] = useState<string>('')
  const filteredContent = searchSubscriptions(searchQuery)

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon">
          <Settings />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Настроить дашборд</DialogTitle>
          <DialogDescription>
            Выберите, какие котировки отображать на дашборде
          </DialogDescription>
        </DialogHeader>
        <Input
          placeholder="Поиск по котировкам..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <div className="flex flex-col gap-4 py-4 h-[260px] lg:h-[360px] xl:h-[420px] overflow-y-auto">
          {filteredContent.map((section) => (
            <div key={section.section_name} className="mb-4">
              <h2 className="text-xl font-semibold">{section.section_name}</h2>
              {section.subscription_items.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between py-2 border-b"
                >
                  <div className="flex items-center">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleActiveToggle(item.id)}
                    >
                      {item.active ? (
                        <Eye className="w-5 h-5" />
                      ) : (
                        <EyeOff className="w-5 h-5" />
                      )}
                    </Button>
                    <span
                      className={`ml-2 ${!item.active ? 'opacity-50' : ''}`}
                    >
                      {item.name}
                    </span>
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      variant={item.type === 1 ? 'secondary' : 'ghost'}
                      size="icon"
                      disabled={!item.active}
                      onClick={() => handleTypeChange(item.id, 1)}
                    >
                      <List className="w-5 h-5" />
                    </Button>
                    <Button
                      variant={item.type === 2 ? 'secondary' : 'ghost'}
                      size="icon"
                      disabled={!item.active}
                      onClick={() => handleTypeChange(item.id, 2)}
                    >
                      <Grid2X2 className="w-5 h-5" />
                    </Button>
                    <Button
                      variant={item.type === 3 ? 'secondary' : 'ghost'}
                      size="icon"
                      disabled={!item.active}
                      onClick={() => handleTypeChange(item.id, 3)}
                    >
                      <Square className="w-6 h-6" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button onClick={handleSave}>Сохранить</Button>
          </DialogClose>
          <Button variant="outline" onClick={handleCancel}>
            Отменить
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export { ManageDashboardButton }
