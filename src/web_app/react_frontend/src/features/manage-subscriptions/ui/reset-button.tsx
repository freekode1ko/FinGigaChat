import { resetSubscriptions } from '@/entities/subscriptions'
import { useAppDispatch } from '@/shared/lib'
import { Button } from '@/shared/ui'

const ResetSubscriptionsButton = () => {
  const dispatch = useAppDispatch()

  return (
    <Button
      className="w-full"
      onClick={() => dispatch(resetSubscriptions())}
      variant="outline"
    >
      Сброс
    </Button>
  )
}

export { ResetSubscriptionsButton }
