import { EllipsisVertical } from 'lucide-react'

import { UploadCommodityResearchDialog } from '@/features/commodities/upload-analytics'
import { type Commodity, useGetCommoditiesQuery } from '@/entities/commodity'
import {
  DataTable,
  DataTablePagination,
  DataTableSearch,
  Loading,
} from '@/shared/kit'
import {
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  TypographyH2,
} from '@/shared/ui'
import {
  type ColumnDef,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  useReactTable,
} from '@tanstack/react-table'

const columns: Array<ColumnDef<Commodity>> = [
  {
    id: 'name',
    header: 'Название',
    accessorKey: 'name',
  },
  {
    id: 'commodity_research',
    header: 'Аналитика',
    accessorKey: 'commodity_research',
    cell: ({ row }) => <p>{row.original.commodity_research.length}</p>,
  },
  {
    id: 'actions',
    header: '',
    accessorKey: 'actions',
    cell: ({ row }) => {
      return (
        <div className="flex justify-end">
          <ManageCommoditiesDropdown commodity={row.original} />
        </div>
      )
    },
  },
]

const AdminCommoditiesPage = () => {
  const { data: commodities, isLoading } = useGetCommoditiesQuery()

  const table = useReactTable({
    data: commodities || [],
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  })

  if (!commodities || isLoading)
    return (
      <Loading
        type="container"
        message={
          <p className="text-lg font-semibold leading-6">Загружаем товары...</p>
        }
      />
    )

  return (
    <div className="p-4">
      <div className="flex justify-between mb-2">
        <TypographyH2>Управление товарами (commodities)</TypographyH2>
      </div>
      <div className="space-y-2">
        <DataTableSearch
          value={(table.getColumn('name')?.getFilterValue() as string) ?? ''}
          onChange={(query) => table.getColumn('name')?.setFilterValue(query)}
          placeholder="Поиск по названию..."
        />
        <DataTable table={table} />
        <DataTablePagination table={table} />
      </div>
    </div>
  )
}

const ManageCommoditiesDropdown = ({ commodity }: { commodity: Commodity }) => {
  return (
    <DropdownMenu modal={false}>
      <DropdownMenuTrigger asChild>
        <Button size="icon" variant="ghost">
          <EllipsisVertical className="h-6 w-6" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56">
        <UploadCommodityResearchDialog commodity={commodity}>
          <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
            Аналитика по товару
          </DropdownMenuItem>
        </UploadCommodityResearchDialog>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export { AdminCommoditiesPage }
