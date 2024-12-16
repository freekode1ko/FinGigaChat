import { Download } from 'lucide-react'

import { UploadResearchForm } from '@/features/commodities/add'
import { type Commodity, type CommodityResearch } from '@/entities/commodity'
import {
  Button,
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  ScrollArea,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/shared/ui'

export const CommodityModal = ({
  action,
  item,
  onClose,
}: {
  action: 'researches'
  item: Commodity | null
  onClose: () => void
}) => {
  return (
    <Dialog open={true} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {action === 'researches' && `Аналитика по ${item?.name}`}
          </DialogTitle>
        </DialogHeader>
        {action === 'researches' ? (
          <Tabs defaultValue="view">
            <TabsList className="w-full">
              <TabsTrigger value="view" className="flex-1">
                Просмотр аналитики
              </TabsTrigger>
              <TabsTrigger value="upload" className="flex-1">
                Загрузить аналитику
              </TabsTrigger>
            </TabsList>
            <TabsContent value="view">
              <ScrollArea className="h-96 rounded-md border">
                <div className="flex flex-col gap-2 justify-center items-center p-2">
                  {item?.commodity_research.length ? (
                    item?.commodity_research.map(
                      (research: CommodityResearch) => (
                        <Research key={research.id} research={research} />
                      )
                    )
                  ) : (
                    <p className="text-foreground">
                      Аналитика публичных рынков не найдена
                    </p>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>
            <TabsContent value="upload">
              <UploadResearchForm commodityId={item!.id} />
            </TabsContent>
          </Tabs>
        ) : null}
      </DialogContent>
    </Dialog>
  )
}

const Research = ({ research }: { research: CommodityResearch }) => {
  return (
    <div className="w-full border p-2 rounded">
      <h3 className="font-bold">
        {research.title ? research.title : 'Нет названия'}
      </h3>
      <div className="flex flex-col gap-2 items-center">
        <p className="mt-2 text-foreground">{research.text}</p>
        <Button variant="ghost" size="sm" asChild>
          <a href={research.url} target="_blank" rel="noreferrer">
            <Download className="h-4 w-4" />
            <span>Скачать</span>
          </a>
        </Button>
      </div>
    </div>
  )
}
