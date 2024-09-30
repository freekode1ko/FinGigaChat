import { Eye, EyeOff, Grid2X2, List, Square } from 'lucide-react'

import type { DashboardSubscriptionSection } from '@/entities/quotes/model'
import {
  Button,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/shared/ui'

interface ManageDashboardButtonProps {
  pageContent: Array<DashboardSubscriptionSection>
  setPageContent: React.Dispatch<
    React.SetStateAction<Array<DashboardSubscriptionSection>>
  >
  handleSave: () => void
  handleCancel: () => void
}

const ManageDashboardButton = ({
  pageContent,
  setPageContent,
  handleSave,
  handleCancel,
}: ManageDashboardButtonProps) => {
  const handleActiveToggle = (sectionIdx: number, itemIdx: number) => {
    setPageContent((prevContent) =>
      prevContent.map((section, sIdx) =>
        sIdx === sectionIdx
          ? {
              ...section,
              subscription_items: section.subscription_items.map(
                (item, iIdx) =>
                  iIdx === itemIdx ? { ...item, active: !item.active } : item
              ),
            }
          : section
      )
    )
  }

  const handleTypeChange = (
    sectionIdx: number,
    itemIdx: number,
    newType: number
  ) => {
    setPageContent((prevContent) =>
      prevContent.map((section, sIdx) =>
        sIdx === sectionIdx
          ? {
              ...section,
              subscription_items: section.subscription_items.map(
                (item, iIdx) =>
                  iIdx === itemIdx ? { ...item, type: newType } : item
              ),
            }
          : section
      )
    )
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">Настроить дашборд</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Настроить дашборд</DialogTitle>
          <DialogDescription>
            Вы можете выбрать, как отображать финансовые данные: в строчку, в
            виде маленького или большого графика.
          </DialogDescription>
        </DialogHeader>
        <div className="flex flex-col gap-4 py-4 max-h-96 overflow-y-auto">
          {pageContent.map((section, sectionIdx) => (
            <div key={section.section_name} className="mb-4">
              <h2 className="text-xl font-semibold">{section.section_name}</h2>
              {section.subscription_items.map((item, itemIdx) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between py-2 border-b"
                >
                  <div className="flex items-center">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleActiveToggle(sectionIdx, itemIdx)}
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
                      onClick={() => handleTypeChange(sectionIdx, itemIdx, 1)}
                    >
                      <List className="w-5 h-5" />
                    </Button>
                    <Button
                      variant={item.type === 2 ? 'secondary' : 'ghost'}
                      size="icon"
                      disabled={!item.active}
                      onClick={() => handleTypeChange(sectionIdx, itemIdx, 2)}
                    >
                      <Grid2X2 className="w-5 h-5" />
                    </Button>
                    <Button
                      variant={item.type === 3 ? 'secondary' : 'ghost'}
                      size="icon"
                      disabled={!item.active}
                      onClick={() => handleTypeChange(sectionIdx, itemIdx, 3)}
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
          <Button onClick={handleSave}>Сохранить</Button>
          <Button variant="outline" onClick={handleCancel}>
            Отменить
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export { ManageDashboardButton }
