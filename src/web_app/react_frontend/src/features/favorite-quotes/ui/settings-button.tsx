import { Settings } from 'lucide-react'
import { useState } from 'react'

import {
  selectFavoriteQuotesList,
  TRADINGVIEW_QUOTES,
  type TradingViewSymbol,
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

import { MAX_QUOTES_QTY, MIN_QUOTES_QTY } from '../model'

// Нужна декомпозиция

const FavoriteQuotesSettings = () => {
  const dispatch = useAppDispatch()
  const favoriteQuotes = useAppSelector(selectFavoriteQuotesList)
  const [selectedQuotes, setSelectedQuotes] =
    useState<Array<TradingViewSymbol>>(favoriteQuotes)
  const handleCheckboxChange = (symbol: TradingViewSymbol) => {
    setSelectedQuotes((prevSelectedQuotes) => {
      if (
        prevSelectedQuotes.some(
          (selectedQuote) => selectedQuote.id === symbol.id
        )
      ) {
        return prevSelectedQuotes.filter(
          (selectedQuote) => selectedQuote.id !== symbol.id
        )
      } else {
        return [...prevSelectedQuotes, symbol]
      }
    })
  }
  const isCheckboxDisabled = (symbol: TradingViewSymbol) => {
    return (
      (!selectedQuotes.some(
        (selectedQuote) => selectedQuote.id === symbol.id
      ) &&
        selectedQuotes.length >= MAX_QUOTES_QTY) ||
      (selectedQuotes.some((selectedQuote) => selectedQuote.id === symbol.id) &&
        selectedQuotes.length <= MIN_QUOTES_QTY)
    )
  }

  return (
    <Drawer>
      <DrawerTrigger asChild>
        <Button variant="ghost" size="icon">
          <Settings />
        </Button>
      </DrawerTrigger>
      <DrawerContent>
        <div className="mx-auto w-full max-w-sm">
          <DrawerHeader>
            <DrawerTitle>Избранные котировки</DrawerTitle>
            <DrawerDescription>
              Вы можете выбрать от {MIN_QUOTES_QTY} до {MAX_QUOTES_QTY}{' '}
              котировок
            </DrawerDescription>
          </DrawerHeader>
          <div className="p-4 pb-0">
            <div className="flex flex-col gap-4 max-h-80 overflow-y-auto">
              {TRADINGVIEW_QUOTES.map((symbol) => (
                <div className="flex items-center gap-2" key={symbol.id}>
                  <Checkbox
                    id={symbol.id}
                    checked={selectedQuotes.some(
                      (selectedQuote) => selectedQuote.id === symbol.id
                    )}
                    onCheckedChange={() => handleCheckboxChange(symbol)}
                    disabled={isCheckboxDisabled(symbol)}
                  />
                  <Label htmlFor={symbol.id}>{symbol.name}</Label>
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
              <Button
                variant="outline"
                className="w-full"
                onClick={() => setSelectedQuotes(favoriteQuotes)}
              >
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
