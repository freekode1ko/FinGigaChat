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
    <Input
      placeholder={placeholder}
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  )
}
