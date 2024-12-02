import { ChevronDown, ChevronRight } from 'lucide-react'
import { useState } from 'react'
import React from 'react'

import { ProductModal } from '@/widgets/products-modal'
import { type Product, useGetProductsTreeQuery } from '@/entities/products'
import { cn } from '@/shared/lib'
import {
  Button,
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
  TypographyH2,
} from '@/shared/ui'

const AdminHomePage = () => {
  const { data } = useGetProductsTreeQuery()
  const [modalState, setModalState] = useState<{
    action: 'create' | 'edit' | 'delete' | 'documents' | null
    item: Product | null
  }>({ action: null, item: null })
  const handleCreate = () => setModalState({ action: 'create', item: null })
  const handleEdit = (item: Product) => setModalState({ action: 'edit', item })
  const handleDelete = (item: Product) =>
    setModalState({ action: 'delete', item })
  const handleDocuments = (item: Product) =>
    setModalState({ action: 'documents', item })

  if (!data) return <div>loading...</div>
  return (
    <div className="p-4">
      <div className="flex justify-between mb-2">
        <TypographyH2>Управление продуктами</TypographyH2>
        <Button onClick={handleCreate}>Добавить продукт</Button>
      </div>
      <ProductTree
        data={data}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onDocuments={handleDocuments}
      />
      {modalState.action && (
        <ProductModal
          action={modalState.action}
          item={modalState.item}
          onClose={() => setModalState({ action: null, item: null })}
        />
      )}
    </div>
  )
}

const ProductTree = ({
  data,
  onEdit,
  onDelete,
  onDocuments,
}: {
  data: Array<Product>
  onEdit: (item: Product) => void
  onDelete: (item: Product) => void
  onDocuments: (item: Product) => void
}) => {
  return (
    <div className="w-full">
      {data.map((item) => (
        <ProductNode
          key={item.id}
          item={item}
          level={0}
          onEdit={onEdit}
          onDelete={onDelete}
          onDocuments={onDocuments}
        />
      ))}
    </div>
  )
}

const ProductNode = ({
  item,
  level,
  onEdit,
  onDelete,
  onDocuments,
}: {
  item: Product
  level: number
  onEdit: (item: Product) => void
  onDelete: (item: Product) => void
  onDocuments: (item: Product) => void
}) => {
  const [isExpanded, setIsExpanded] = React.useState(false)

  return (
    <div className={cn('space-y-2', `pl-${level * 4}`)}>
      <div className="flex items-center justify-between py-2 px-3 rounded-md hover:bg-secondary">
        <div className="flex items-center">
          {item.children.length > 0 && (
            <button
              onClick={() => setIsExpanded((prev) => !prev)}
              aria-label={isExpanded ? 'Свернуть' : 'Развернуть'}
              className="mr-2"
            >
              {isExpanded ? (
                <ChevronDown size={20} />
              ) : (
                <ChevronRight size={20} />
              )}
            </button>
          )}
          <ContextMenu modal={false}>
            <ContextMenuTrigger asChild>
              <p className="text-xl font-medium cursor-pointer">{item.name}</p>
            </ContextMenuTrigger>
            <ContextMenuContent>
              <ContextMenuItem onSelect={() => onDocuments(item)}>
                Документы
              </ContextMenuItem>
              <ContextMenuItem onSelect={() => onEdit(item)}>
                Редактировать
              </ContextMenuItem>
              <ContextMenuItem onSelect={() => onDelete(item)}>
                Удалить
              </ContextMenuItem>
            </ContextMenuContent>
          </ContextMenu>
        </div>
      </div>
      {isExpanded && item.children.length > 0 && (
        <div className="space-y-2">
          {item.children.map((child) => (
            <ProductNode
              key={child.id}
              item={child}
              level={level + 1}
              onEdit={onEdit}
              onDelete={onDelete}
              onDocuments={onDocuments}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export { AdminHomePage }
