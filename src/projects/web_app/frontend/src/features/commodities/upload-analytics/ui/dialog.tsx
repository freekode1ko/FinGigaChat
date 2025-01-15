import { useState } from 'react'

import { type Commodity, CommodityResearch } from '@/entities/commodity'
import { AdaptableModal } from '@/shared/kit'
import {
  ScrollArea,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/shared/ui'

import { UploadResearchForm } from './form'

const UploadCommodityResearchDialog = ({
  commodity,
  children,
}: {
  commodity: Commodity
  children: React.ReactNode
}) => {
  const [open, setOpen] = useState(false)
  return (
    <AdaptableModal
      open={open}
      onOpenChange={setOpen}
      title={`Аналитика по ${commodity.name}`}
      trigger={children}
    >
      <Tabs defaultValue="view">
        <TabsList className="w-full bg-secondary">
          <TabsTrigger value="view" className="flex-1">
            Просмотр аналитики
          </TabsTrigger>
          <TabsTrigger value="upload" className="flex-1">
            Добавить аналитику
          </TabsTrigger>
        </TabsList>
        <TabsContent value="view">
          <ScrollArea className="h-96 rounded-md border">
            <div className="flex flex-col gap-2 justify-center industrys-center p-2">
              {commodity?.commodity_research.length ? (
                commodity?.commodity_research.map((research) => (
                  <CommodityResearch key={research.id} research={research} />
                ))
              ) : (
                <p className="text-foreground">
                  Аналитика по товару не найдена
                </p>
              )}
            </div>
          </ScrollArea>
        </TabsContent>
        <TabsContent value="upload">
          <UploadResearchForm
            commodityId={commodity!.id}
            onSuccess={() => setOpen(false)}
          />
        </TabsContent>
      </Tabs>
    </AdaptableModal>
  )
}

export { UploadCommodityResearchDialog }
