import { useState } from 'react'

import { type Product, ProductDocument } from '@/entities/products'
import { AdaptableModal } from '@/shared/kit'
import {
  ScrollArea,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/shared/ui'

import { DeleteProductDocumentButton } from '../../delete' // fix
import { UploadDocumentForm } from './form'

const UploadProductDocumentDialog = ({
  product,
  children,
}: {
  product: Product
  children: React.ReactNode
}) => {
  const [open, setOpen] = useState(false)
  return (
    <AdaptableModal
      open={open}
      onOpenChange={setOpen}
      title={`Документы для ${product.name}`}
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
            <div className="flex flex-col gap-2 justify-center items-center p-2">
              {product?.documents.length ? (
                product?.documents.map((doc) => (
                  <ProductDocument key={doc.id} doc={doc} actionSlot={<DeleteProductDocumentButton id={doc.id} />} />
                ))
              ) : (
                <p className="text-foreground">
                  Документы по продукту не найдены
                </p>
              )}
            </div>
          </ScrollArea>
        </TabsContent>
        <TabsContent value="upload">
          <UploadDocumentForm
            productId={product!.id}
            onSuccess={() => setOpen(false)}
          />
        </TabsContent>
      </Tabs>
    </AdaptableModal>
  )
}

export { UploadProductDocumentDialog }
