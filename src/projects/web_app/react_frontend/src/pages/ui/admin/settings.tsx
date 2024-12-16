import { PencilIcon } from 'lucide-react'
import { useMemo,useState } from 'react'
import { toast } from 'sonner'

import { type Setting, useGetSettingsQuery, useSetSettingMutation } from '@/entities/settings'
import { AdaptableModal, DataTable, DataTablePagination } from '@/shared/kit'
import { useMediaQuery } from '@/shared/lib'
import { DESKTOP_MEDIA_QUERY } from '@/shared/model'
import { Button, Textarea } from '@/shared/ui'
import { type ColumnDef, getCoreRowModel, getPaginationRowModel, useReactTable } from "@tanstack/react-table"

const SettingEdit = ({ setting }: { setting: Setting }) => {
  const [trigger] = useSetSettingMutation()
  const [newValue, setNewValue] = useState(setting.value)
  const [open, setOpen] = useState(false)
  const handleSave = () => {
    toast.promise(trigger({ key: setting.key, newValue }).unwrap(), {
      loading: 'Сохраняем изменения...',
      success: () => {
        setOpen(false)
        return 'Изменения сохранены!'
      },
      error: 'Мы не смогли сохранить изменения. Попробуйте позже.',
    })
  }

  return (
    <AdaptableModal
      open={open}
      onOpenChange={setOpen}
      trigger={
        <Button variant="outline" size="icon">
          <PencilIcon className="w-4 h-4" />
        </Button>
      }
    >
      <div className="space-y-4">
        <h4 className="font-medium leading-none">{setting.name}</h4>
        <p className="text-sm text-muted-foreground">{setting.key}</p>
        <Textarea
          value={newValue}
          onChange={(e) => setNewValue(e.target.value)}
        />
        <Button onClick={handleSave}>Сохранить</Button>
      </div>
    </AdaptableModal>
  )
}

export function AdminSettingsPage() {
  const isDesktop = useMediaQuery(DESKTOP_MEDIA_QUERY)
  const { data: settings, isLoading } = useGetSettingsQuery()

  const columns = useMemo(() => {
    const baseColumns: Array<ColumnDef<Setting>> = [
      {
        accessorKey: "name",
        header: "Название",
      },
      {
        accessorKey: "actions",
        header: undefined,
        cell: ({ row }) => <SettingEdit setting={row.original} />,
      },
    ]

    if (isDesktop) {
      return [
        ...baseColumns.slice(0, 1),
        {
          accessorKey: "key",
          header: "Ключ",
        },
        {
          accessorKey: "value",
          header: "Значение",
          cell: ({ row }) => (
            <div className="max-w-[500px] truncate">{row.original.value}</div>
          ),
        },
        baseColumns[1],
      ]
    }

    return baseColumns
  }, [isDesktop])

  const table = useReactTable({
    data: settings || [],
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  })

  if (isLoading) {
    return <div>Загрузка...</div>
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Настройки бота</h1>
      </div>
      <div className='space-y-2'>
        <DataTable table={table} />
        <DataTablePagination table={table} />
      </div>
    </div>
  )
}
