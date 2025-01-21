import { Check, ChevronsUpDown } from "lucide-react"
import React, { useRef } from 'react'

import { cn } from '@/shared/lib'
import {
  Button,
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  Popover,
  PopoverContent,
  PopoverTrigger
} from "@/shared/ui"

export interface ComboboxItem {
  id: string | number
  name: string
}

interface ComboboxProps {
  items: Array<ComboboxItem>
  value: string | number | Array<string | number> | null
  onChange: (newValue: string | number | Array<string | number>) => void
  multiSelect?: boolean
  placeholder?: string
}

export function Combobox({
  items,
  value,
  onChange,
  multiSelect = false,
  placeholder = 'Выберите...',
}: ComboboxProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [open, setOpen] = React.useState(false)
  const [searchTerm, setSearchTerm] = React.useState('')

  const selectedValues = React.useMemo(() => {
    if (multiSelect) {
      return Array.isArray(value) ? value : []
    }
    return value ? [value] : []
  }, [multiSelect, value])

  const filteredItems = React.useMemo(() => {
    if (!searchTerm) return items
    return items.filter(item => 
      item.name.toLowerCase().includes(searchTerm.toLowerCase())
    )
  }, [items, searchTerm])

  const handleSelect = (item: ComboboxItem) => {
    if (!multiSelect) {
      onChange(item.id)
      setOpen(false)
      return
    }
    if (Array.isArray(value)) {
      if (value.includes(item.id)) {
        onChange(value.filter((id) => id !== item.id))
      } else {
        onChange([...value, item.id])
      }
    } else {
      onChange([item.id])
    }
  }

  const selectedItemsCount = multiSelect
    ? Array.isArray(value)
      ? value.length
      : 0
    : 0

  const displayValue = React.useMemo(() => {
    if (multiSelect) {
      return selectedItemsCount > 0
        ? `${selectedItemsCount} выбрано`
        : placeholder
    } else {
      const selectedItem = items.find(i => i.id === value)
      return selectedItem ? selectedItem.name : placeholder
    }
  }, [multiSelect, value, items, placeholder, selectedItemsCount])

  return (
    <div ref={containerRef} className="shrink-0">
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className={cn(
              'w-full justify-between text-wrap whitespace-normal text-left',
              !selectedValues.length && 'text-muted-foreground'
            )}
          >
            {displayValue}
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent
          className="min-w-full p-0"
          container={containerRef?.current} 
        >
          <Command>
            <CommandInput
              placeholder="Поиск..."
              value={searchTerm}
              onValueChange={setSearchTerm}
            />
            <CommandList>
              <CommandEmpty>Ничего не найдено</CommandEmpty>
              <CommandGroup>
                {filteredItems.map(item => {
                  const isSelected = selectedValues.includes(item.id)
                  return (
                    <CommandItem
                      key={item.id}
                      value={item.name}
                      onSelect={() => handleSelect(item)}
                    >
                      <Check
                        className={cn(
                          'mr-2 h-4 w-4',
                          isSelected ? 'opacity-100' : 'opacity-0'
                        )}
                      />
                      {item.name}
                    </CommandItem>
                  )
                })}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  )
}
