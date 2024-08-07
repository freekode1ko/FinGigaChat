import { Settings } from 'lucide-react'
import { useState } from 'react'

import {
  POPULAR_QUOTES,
  type PopularQuotes,
  selectFavoriteQuotesList,
  updateFavoriteQuotesList,
} from '@/entities/quotes'
import { useAppDispatch, useAppSelector } from '@/shared/lib'
import {
  Button,
  Checkbox,
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
  Label,
} from '@/shared/ui'

// Нужна декомпозиция

const FavoriteQuotesSettings = () => {
  const favoriteQuotes = useAppSelector(selectFavoriteQuotesList)
  const [selectedQuotes, setSelectedQuotes] =
    useState<Array<PopularQuotes>>(favoriteQuotes)
  const dispatch = useAppDispatch()
  const handleCheckboxChange = (symbol: PopularQuotes) => {
    setSelectedQuotes((prev) =>
      prev.includes(symbol)
        ? prev.filter((s) => s !== symbol)
        : [...prev, symbol]
    )
  }

  return (
    <Drawer>
      <DrawerTrigger asChild>
        <Button variant="outline" size="icon" className="border-none">
          <Settings />
        </Button>
      </DrawerTrigger>
      <DrawerContent>
        <div className="mx-auto w-full max-w-sm">
          <DrawerHeader>
            <DrawerTitle>Избранные котировки</DrawerTitle>
            <DrawerDescription>
              Вы можете выбрать до 4 котировок
            </DrawerDescription>
          </DrawerHeader>
          <div className="p-4 pb-0">
            <div className="flex flex-col gap-4 max-h-80 overflow-y-auto">
              {POPULAR_QUOTES.map((symbol) => (
                <div className="flex items-center gap-2" key={symbol}>
                  <Checkbox
                    id={symbol}
                    checked={selectedQuotes.includes(symbol)}
                    onCheckedChange={() => handleCheckboxChange(symbol)}
                    disabled={
                      !selectedQuotes.includes(symbol) &&
                      selectedQuotes.length >= 4
                    }
                  />
                  <Label htmlFor={symbol}>{symbol}</Label>
                </div>
              ))}
            </div>
          </div>
          <DrawerFooter>
            <DrawerClose asChild>
              <Button
                className="w-full"
                onClick={() =>
                  dispatch(updateFavoriteQuotesList(selectedQuotes))
                }
              >
                Сохранить
              </Button>
            </DrawerClose>
            <DrawerClose asChild>
              <Button variant="outline" className="w-full">
                Отменить
              </Button>
            </DrawerClose>
          </DrawerFooter>
        </div>
      </DrawerContent>
    </Drawer>
  )
}

export { FavoriteQuotesSettings }
