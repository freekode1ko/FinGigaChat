import { Info, Upload } from 'lucide-react'
import { useCallback, useMemo, useState } from 'react'

import {
  useGetFlatUsersQuery,
  useGetUserRolesQuery,
  type User,
} from '@/entities/user'
import {
  Combobox,
  DataTable,
  DataTablePagination,
  DataTableSearch,
  Loading,
} from '@/shared/kit'
import {
  Button,
  Checkbox,
  FileInput,
  FileUploader,
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/shared/ui'
import {
  type ColumnDef,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  type OnChangeFn,
  RowSelectionState,
  useReactTable,
} from '@tanstack/react-table'

const columns: Array<ColumnDef<User>> = [
  {
    id: 'select',
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && 'indeterminate')
        }
        onCheckedChange={(value) => table.toggleAllRowsSelected(!!value)}
      />
    ),
    cell: ({ row }) => (
      <div className="px-1">
        <Checkbox
          checked={row.getIsSelected()}
          onCheckedChange={(value) => row.toggleSelected(!!value)}
          disabled={!row.getCanSelect()}
        />
      </div>
    ),
  },
  {
    accessorKey: 'email',
    header: 'Email',
  },
  {
    accessorKey: 'role',
    header: 'Роль',
    filterFn: (row, columnId, filterValue: string[]) => {
      if (!filterValue || filterValue.length === 0) return true
      const rowValue = row.getValue(columnId) as string
      return filterValue.includes(rowValue)
    },
  },
]

type ReceiverSelectorProps = {
  value: string[]
  onChange: (newSelectedEmails: string[]) => void
}

export const ReceiverSelector = ({ value, onChange }: ReceiverSelectorProps) => {
  const { data: roles, isLoading: isLoadingRoles } = useGetUserRolesQuery()
  const { data: users, isLoading: isLoadingUsers } = useGetFlatUsersQuery()
  const [uploadedFiles, setUploadedFiles] = useState<File[] | null>(null)

  const rowSelection = useMemo<RowSelectionState>(() => {
    if (!users) return {}
    const selection: RowSelectionState = {}
    for (const user of users) {
      if (value.includes(user.email)) {
        selection[user.email] = true
      }
    }
    return selection
  }, [users, value])

  const setRowSelection = useCallback<OnChangeFn<RowSelectionState>>(
    (updaterOrValue) => {
      const newSelection =
        typeof updaterOrValue === 'function'
          ? updaterOrValue(rowSelection)
          : updaterOrValue
      const selectedEmails = Object.keys(newSelection).filter(
        (email) => newSelection[email] === true
      )
      onChange(selectedEmails)
    },
    [rowSelection, onChange]
  )

  const table = useReactTable({
    data: users ?? [],
    columns,
    state: { rowSelection },
    enableRowSelection: true,
    getRowId: (user) => user.email,
    onRowSelectionChange: setRowSelection,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  })

  const handleFileChange = useCallback(
    async (newFiles: File[] | null) => {
      setUploadedFiles(newFiles)
      if (!newFiles || newFiles.length === 0) return
      const file = newFiles[0]
      const text = await file.text()
      const fileEmails = text
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter(Boolean)
      onChange(fileEmails)
      setUploadedFiles(null)
    },
    [onChange]
  )

  if (!users || isLoadingUsers || isLoadingRoles) {
    return (
      <Loading
        type="container"
        message={<p className="text-lg font-semibold">Загружаем пользователей...</p>}
      />
    )
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 shrink-0">
        <FileUploader
          value={uploadedFiles}
          onValueChange={handleFileChange}
          dropzoneOptions={{
            accept: { 'text/plain': ['.txt'] },
            multiple: false,
          }}
        >
          <FileInput className="w-auto">
            <Button variant="outline" className="w-full lg:w-auto">
              <Upload className="h-4 w-4" />
              <span>Загрузить из файла</span>
            </Button>
          </FileInput>
        </FileUploader>

        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon">
                <Info className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent className="max-w-xs">
              <p>Почтовые адреса должны быть перечислены в текстовом файле с переносом строки.</p>
              <p className="mt-2 mb-1">Пример:</p>
              <code className="text-sm">
                пользователь-1@sberbank.ru
                <br />
                пользователь-2@sberbank.ru
              </code>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>

      <div className="flex flex-row gap-2 mb-4">
        <DataTableSearch
          value={(table.getColumn('email')?.getFilterValue() as string) ?? ''}
          onChange={(query) => table.getColumn('email')?.setFilterValue(query)}
          placeholder="Поиск по E-Mail..."
        />
        <Combobox
          multiSelect
          items={roles ?? []}
          value={table.getColumn('role')?.getFilterValue() as number[]}
          onChange={(value) => table.getColumn('role')?.setFilterValue(value)}
          placeholder="Фильтр по ролям..."
        />
      </div>

      <DataTable table={table} />
      <div className="flex flex-col md:flex-row items-center justify-between gap-4">
        <p>
          Выбрано пользователей: {Object.keys(rowSelection).length} из{' '}
          {table.getPreFilteredRowModel().rows.length}
        </p>
        <DataTablePagination table={table} />
      </div>
    </div>
  )
}
