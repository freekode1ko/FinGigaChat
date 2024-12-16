import { useState } from 'react'

import { CreateWhitelistDialog } from '@/features/whitelist/add'
import { DeleteFromWhitelistDialog } from '@/features/whitelist/delete'
import { useGetWhitelistQuery, type WhitelistUser } from '@/entities/whitelist'
import { DataTable, DataTablePagination, DataTableSearch } from '@/shared/kit'
import { type ColumnDef, getCoreRowModel,useReactTable } from "@tanstack/react-table"

const columns: Array<ColumnDef<WhitelistUser>> = [
  {
    accessorKey: "email",
    header: "Email",
  },
  {
    accessorKey: "actions",
    header: undefined,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <DeleteFromWhitelistDialog email={row.original.email} />
      </div>
    ),
  },
]

export function AdminWhitelistPage() {
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 })
  const [emailFilter, setEmailFilter] = useState('')

  const { data: whitelist, isLoading } = useGetWhitelistQuery({
    page: pagination.pageIndex + 1,
    size: pagination.pageSize,
    email: emailFilter.length > 0 ? emailFilter : undefined,
  })

  const table = useReactTable({
    data: whitelist?.items || [],
    columns,
    getCoreRowModel: getCoreRowModel(),
    pageCount: whitelist?.total_pages || 1,
    state: {
      pagination,
    },
    manualPagination: true,
    onPaginationChange: setPagination,
  })

  if (isLoading) {
    return <div>Загрузка...</div>
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Управление белым списком</h1>
        <CreateWhitelistDialog />
      </div>
      <div className='space-y-2'>
        <DataTableSearch
          value={emailFilter}
          onChange={(value) => {
            setEmailFilter(value)
            setPagination(prev => ({ ...prev, pageIndex: 0 }))
          }}
          placeholder="Поиск по E-Mail..."
        />
        <DataTable table={table} />
        <DataTablePagination table={table} />
      </div>
    </div>
  )
}
