import { Eye, EyeOff } from 'lucide-react'

import {
  selectIsFavoriteQuotesShown,
  toggleFavoriteQuotes,
} from '@/entities/quotes'
import { useAppDispatch, useAppSelector } from '@/shared/lib'
import { Button } from '@/shared/ui'

const FavoriteQuotesToggler = () => {
  const isFavoriteQuotesShown = useAppSelector(selectIsFavoriteQuotesShown)
  const dispatch = useAppDispatch()

  return (
    <Button
      variant="outline"
      size="icon"
      className="border-none"
      onClick={() => dispatch(toggleFavoriteQuotes())}
    >
      {isFavoriteQuotesShown ? <Eye /> : <EyeOff />}
    </Button>
  )
}

export { FavoriteQuotesToggler }
