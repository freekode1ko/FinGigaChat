import { EllipsisVertical } from 'lucide-react'
import { useState } from 'react'

import { CommodityModal } from '@/widgets/commodities-modal'
import { type Commodity, useGetCommoditiesQuery } from '@/entities/commodity'
import { Loading } from '@/shared/kit'
import {
  Button,
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  TypographyH2,
} from '@/shared/ui'

const AdminCommoditiesPage = () => {
  const { data: commodities } = useGetCommoditiesQuery()
  const [modalState, setModalState] = useState<{
    action: Optional<'researches'>
    item: Optional<Commodity>
  }>({ action: null, item: null })

  if (!commodities)
    return (
      <Loading
        type="container"
        message={
          <p className="text-lg font-semibold leading-6">
            Загружаем commodities...
          </p>
        }
      />
    )
  return (
    <div className="p-4">
      <div className="flex justify-between mb-2">
        <TypographyH2>Управление commodities</TypographyH2>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 pt-4">
        {commodities.map((commodity) => (
          <Card key={commodity.id} className="border border-border">
            <div className="flex justify-between gap-2 p-2">
              <CardHeader className="flex-grow">
                <CardTitle className="truncate">{commodity.name}</CardTitle>
                <CardDescription>
                  Аналитических отчетов: {commodity.commodity_research.length}
                </CardDescription>
              </CardHeader>
              <DropdownMenu modal={false}>
                <DropdownMenuTrigger asChild>
                  <Button size="icon" variant="ghost">
                    <EllipsisVertical className="h-6 w-6" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56">
                  <DropdownMenuItem
                    onSelect={() =>
                      setModalState({ action: 'researches', item: commodity })
                    }
                  >
                    Посмотреть аналитику
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </Card>
        ))}
      </div>
      {modalState.action && (
        <CommodityModal
          action={modalState.action}
          item={modalState.item}
          onClose={() => setModalState({ action: null, item: null })}
        />
      )}
    </div>
  )
}

export { AdminCommoditiesPage }
