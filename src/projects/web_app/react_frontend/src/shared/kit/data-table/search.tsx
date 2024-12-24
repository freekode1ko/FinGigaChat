import { Input } from '@/shared/ui'

interface DataTableSearchProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
}

export function DataTableSearch({
  value,
  onChange,
  placeholder = 'Поиск...',
}: DataTableSearchProps) {
  return (
    <div className="flex items-center py-2">
      <Input
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="max-w-sm"
      />
    </div>
  )
}
