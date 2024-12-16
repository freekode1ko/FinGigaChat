import { useState } from "react"

import { type Industry,IndustryDocument } from "@/entities/industries"
import { AdaptableModal } from "@/shared/kit"
import { ScrollArea,Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/ui"

import { UploadIndustryDocumentForm } from "./form"

const UploadIndustryDocumentDialog = ({industry, children}: {industry: Industry, children: React.ReactNode}) => {
  const [open, setOpen] = useState(false)
  return (
    <AdaptableModal
      open={open}
      onOpenChange={setOpen}
      title={`Документы для ${industry.name}`}
      trigger={children}
    >
      <Tabs defaultValue="view">
        <TabsList className="w-full bg-secondary">
          <TabsTrigger value="view" className="flex-1">
            Просмотр документов
          </TabsTrigger>
          <TabsTrigger value="upload" className="flex-1">
            Загрузить документ
          </TabsTrigger>
        </TabsList>
        <TabsContent value="view">
          <ScrollArea className="h-96 rounded-md border">
            <div className="flex flex-col gap-2 justify-center industrys-center p-2">
              {industry?.documents.length ? (
                industry?.documents.map((doc) => (
                  <IndustryDocument key={doc.id} doc={doc} />
                ))
              ) : (
                <p className="text-foreground">Документы по отрасли не найдены</p>
              )}
            </div>
          </ScrollArea>
        </TabsContent>
        <TabsContent value="upload">
          <UploadIndustryDocumentForm
            industryId={industry!.id}
            onSuccess={() => setOpen(false)}
          />
        </TabsContent>
      </Tabs>
    </AdaptableModal>
  )
}

export { UploadIndustryDocumentDialog }
