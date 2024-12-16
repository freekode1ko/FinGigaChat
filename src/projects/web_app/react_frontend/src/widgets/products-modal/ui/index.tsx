import { Download, Eye, EyeOff } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'

import { CreateProductForm, UploadDocumentForm } from '@/features/products/add'
import { Product, useDeleteProductMutation } from '@/entities/products'
import type { ProductDocument } from '@/entities/products/model/types'
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

export const ProductModal = ({
  action,
  item,
  onClose,
}: {
  action: 'create' | 'edit' | 'delete' | 'documents'
  item: Product | null
  onClose: () => void
}) => {
  const [deleteProduct] = useDeleteProductMutation()

  const handleDelete = () => {
    if (item) {
      toast.promise(deleteProduct({ id: item.id }).unwrap(), {
        loading: `Удаляем ${item.name}...`,
        success: 'Продукт успешно удален!',
        error: 'Мы не смогли удалить продукт. Попробуйте позже.',
      })
    }
  }

  return (
    <Dialog open={true} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {action === 'create' && 'Создать новый продукт'}
            {action === 'edit' && `Редактировать продукт ${item?.name}`}
            {action === 'delete' && `Удалить продукт ${item?.name}`}
            {action === 'documents' && `Документы продукта ${item?.name}`}
          </DialogTitle>
        </DialogHeader>
        {action === 'create' || action === 'edit' ? (
          <CreateProductForm
            item={item}
            onSuccess={() => {
              onClose()
            }}
          />
        ) : action === 'delete' ? (
          <div className="space-y-4">
            <p>Вы уверены, что хотите удалить этот продукт?</p>
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={onClose}>
                Отмена
              </Button>
              <Button variant="destructive" onClick={handleDelete}>
                Удалить
              </Button>
            </div>
          </div>
        ) : action === 'documents' ? (
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
                  {item?.documents.length ? (
                    item?.documents.map((doc: ProductDocument) => (
                      <Document key={doc.id} doc={doc} />
                    ))
                  ) : (
                    <p className="text-foreground">Документы не найдены</p>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>
            <TabsContent value="upload">
              <UploadDocumentForm
                productId={item!.id}
                onSuccess={() => {
                  onClose()
                }}
              />
            </TabsContent>
          </Tabs>
        ) : null}
      </DialogContent>
    </Dialog>
  )
}

const Document = ({ doc }: { doc: ProductDocument }) => {
  const [show, setShow] = useState(false)
  return (
    <div className="w-full border p-2 rounded">
      <h3 className="font-bold">{doc.name}</h3>
      <div className="flex gap-2 items-center">
        <Button variant="ghost" size="sm" asChild>
          <a href={doc.url} target="_blank" rel="noreferrer">
            <Download className="h-4 w-4" />
            <span>Скачать</span>
          </a>
        </Button>
        {doc.description && (
          <Button variant="ghost" size="sm" onClick={() => setShow(!show)}>
            {show ? (
              <EyeOff className="h-4 w-4" />
            ) : (
              <Eye className="h-4 w-4" />
            )}
            <span>{show ? 'Скрыть описание' : 'Показать описание'}</span>
          </Button>
        )}
      </div>
      {doc.description && show && (
        <p className="mt-2 text-foreground">{doc.description}</p>
      )}
    </div>
  )
}
