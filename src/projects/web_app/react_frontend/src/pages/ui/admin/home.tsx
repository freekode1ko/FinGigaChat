import { ChevronDown, ChevronRight, EllipsisVertical } from 'lucide-react'
import { useState } from 'react'
import React from 'react'

import { ProductModal } from '@/widgets/products-modal'
import { type Product, useGetProductsTreeQuery } from '@/entities/products'
import { Loading } from '@/shared/kit'
import {
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
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

  if (!data)
    return (
      <Loading
        type="container"
        message={
          <p className="text-lg font-semibold leading-6">
            Загружаем продукты...
          </p>
        }
      />
    )
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
    <div className="space-y-2">
      <div className="flex items-center justify-between rounded-md hover:bg-secondary px-2">
        <div 
          className="flex items-center flex-grow cursor-pointer py-2" 
          onClick={() => item.children.length > 0 && setIsExpanded((prev) => !prev)}
        >
          <div style={{ paddingLeft: `${level * 1}rem` }} className="flex items-center flex-grow">
            {item.children.length > 0 && (
              <span className="mr-2">
                {isExpanded ? (
                  <ChevronDown size={20} />
                ) : (
                  <ChevronRight size={20} />
                )}
              </span>
            )}
            <p className="text-xl font-medium">{item.name}</p>
          </div>
        </div>
        <div className="px-3">
          <DropdownMenu modal={false}>
            <DropdownMenuTrigger asChild>
              <Button size="icon" variant="ghost">
                <EllipsisVertical className="h-6 w-6" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56">
              <DropdownMenuItem onSelect={() => onDocuments(item)}>
                Документы
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onSelect={() => onEdit(item)}>
                Редактировать
              </DropdownMenuItem>
              <DropdownMenuItem onSelect={() => onDelete(item)}>
                Удалить
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
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
