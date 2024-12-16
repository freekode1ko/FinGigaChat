import { SquarePlus } from 'lucide-react'

import { ManageIndustryDropdown } from '@/widgets/manage-industry-dropdown'
import { CreateIndustryDialog } from '@/features/industries/add'
import { type Industry, useGetIndustriesQuery } from '@/entities/industries'
import { DataTable, DataTablePagination, Loading } from '@/shared/kit'
import { Button } from '@/shared/ui'
import { type ColumnDef, getCoreRowModel, getPaginationRowModel, useReactTable } from '@tanstack/react-table'


const columns: Array<ColumnDef<Industry>> = [
  {
    id: 'name',
    header: 'Название',
    accessorKey: 'name',
  },
  {
    id: 'documents',
    header: 'Документы',
    accessorKey: 'documents',
    cell: ({ row }) => (
      <p>{row.original.documents.length}</p>
    ),
  },
  {
    id: 'actions',
    header: '',
    accessorKey: 'id',
    cell: ({ row }) => {
      return (
        <div className='flex justify-end'>
          <ManageIndustryDropdown industry={row.original} />
        </div>
      )
    },
  },
]

const AdminIndustriesPage = () => {
  const { data: industries, isLoading } = useGetIndustriesQuery()
  const table = useReactTable({
    data: industries || [],
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  })

  if (!industries || isLoading) {
    return (
      <Loading
        type="container"
        message={
          <p className="text-lg font-semibold leading-6">
            Загружаем отрасли...
          </p>
        }
      />
    )
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Управление отраслями</h1>
        <CreateIndustryDialog>
          <Button variant="ghost" size="sm">
            <SquarePlus />
            <span className="hidden md:inline">Добавить отрасль</span>
          </Button>
        </CreateIndustryDialog>
      </div>
      <div className='space-y-2'>
        <DataTable table={table} />
        <DataTablePagination table={table} />
      </div>
    </div>
  )
}

export { AdminIndustriesPage }
