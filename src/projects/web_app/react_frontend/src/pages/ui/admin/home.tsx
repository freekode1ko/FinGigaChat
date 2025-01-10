import {
  ChevronDown,
  ChevronRight,
  EllipsisVertical,
  SquarePlus,
} from 'lucide-react'
import React from 'react'

import { UploadProductDocumentDialog } from '@/features/product-documents/upload'
import { CreateProductDialog } from '@/features/products/add'
import { DeleteProductDialog } from '@/features/products/delete'
import { UpdateProductDialog } from '@/features/products/update'
import { type Product, useGetProductsTreeQuery } from '@/entities/products'
import { Loading } from '@/shared/kit'
import {
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  TypographyH2,
} from '@/shared/ui'

const AdminHomePage = () => {
  const { data } = useGetProductsTreeQuery()

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
        <CreateProductDialog>
          <Button variant="ghost" size="sm">
            <SquarePlus />
            <span className="hidden md:inline">Создать продукт</span>
          </Button>
        </CreateProductDialog>
      </div>
      <ProductTree data={data} />
    </div>
  )
}

const ProductTree = ({ data }: { data: Array<Product> }) => {
  return (
    <div className="w-full">
      {data.map((item) => (
        <ProductNode key={item.id} item={item} level={0} />
      ))}
    </div>
  )
}

const ProductNode = ({ item, level }: { item: Product; level: number }) => {
  const [isExpanded, setIsExpanded] = React.useState(false)

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between rounded-md hover:bg-secondary px-2">
        <div
          className="flex items-center flex-grow cursor-pointer py-2"
          onClick={() =>
            item.children.length > 0 && setIsExpanded((prev) => !prev)
          }
        >
          <div
            style={{ paddingLeft: `${level * 1}rem` }}
            className="flex items-center flex-grow"
          >
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
          <ManageProductDropdown product={item} />
        </div>
      </div>
      {isExpanded && item.children.length > 0 && (
        <div className="space-y-2">
          {item.children.map((child) => (
            <ProductNode key={child.id} item={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  )
}

const ManageProductDropdown = ({ product }: { product: Product }) => {
  return (
    <DropdownMenu modal={false}>
      <DropdownMenuTrigger asChild>
        <Button size="icon" variant="ghost">
          <EllipsisVertical className="h-6 w-6" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56">
        <DropdownMenuLabel>Управление продуктом</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <UpdateProductDialog product={product}>
            <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
              Редактировать
            </DropdownMenuItem>
          </UpdateProductDialog>
          <DeleteProductDialog product={product}>
            <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
              Удалить
            </DropdownMenuItem>
          </DeleteProductDialog>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <UploadProductDocumentDialog product={product}>
            <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
              Документы по продукту
            </DropdownMenuItem>
          </UploadProductDocumentDialog>
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export { AdminHomePage }
