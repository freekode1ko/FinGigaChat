import { PencilIcon } from 'lucide-react'
import { useState } from 'react'

import { UpdateUserRoleDialog } from '@/features/users/update'
import { useGetUsersQuery, type User } from '@/entities/user'
import {
  DataTable,
  DataTablePagination,
  DataTableSearch,
  Loading,
} from '@/shared/kit'
import { Button } from '@/shared/ui'
import {
  type ColumnDef,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table'

const columns: Array<ColumnDef<User>> = [
  {
    accessorKey: 'email',
    header: 'Email',
  },
  {
    accessorKey: 'actions',
    header: undefined,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <UpdateUserRoleDialog user={row.original}>
          <Button variant="outline" size="icon">
            <PencilIcon className="w-4 h-4" />
          </Button>
        </UpdateUserRoleDialog>
      </div>
    ),
  },
]

export function AdminUsersPage() {
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 })
  const [emailFilter, setEmailFilter] = useState<string>('')

  const { data: users, isLoading } = useGetUsersQuery({
    page: pagination.pageIndex + 1,
    size: pagination.pageSize,
    email: emailFilter?.length > 0 ? emailFilter : undefined,
  })

  const table = useReactTable({
    data: users?.items || [],
    columns,
    getCoreRowModel: getCoreRowModel(),
    pageCount: users?.total_pages || 1,
    state: {
      pagination,
    },
    manualPagination: true,
    onPaginationChange: setPagination,
  })

  if (!users || isLoading) {
    return (
      <Loading
        type="container"
        message={
          <p className="text-lg font-semibold leading-6">
            Загружаем пользователей бота...
          </p>
        }
      />
    )
  }
  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Пользователи бота</h1>
      </div>
      <div className="space-y-2">
        <DataTableSearch
          value={emailFilter}
          onChange={(value) => {
            setEmailFilter(value)
            setPagination((prev) => ({ ...prev, pageIndex: 0 }))
          }}
          placeholder="Поиск по E-Mail..."
        />
        <DataTable table={table} />
        <DataTablePagination table={table} />
      </div>
    </div>
  )
}
