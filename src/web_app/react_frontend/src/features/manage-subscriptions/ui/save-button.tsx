import {
  selectSubscriptionsToUpdate,
  useUpdateSubscriptionsMutation,
} from '@/entities/subscriptions'
import { selectUserData } from '@/entities/user'
import { useAppSelector } from '@/shared/lib'
import { Button } from '@/shared/ui'

const SaveSubscriptionsButton = () => {
  const user = useAppSelector(selectUserData)
  const subscriptionsToUpdate = useAppSelector(selectSubscriptionsToUpdate)
  const [trigger, { isLoading }] = useUpdateSubscriptionsMutation()

  const handleSave = async (userId: number) => {
    await trigger({ userId: userId, body: subscriptionsToUpdate }).unwrap()
  }

  if (user) {
    return (
      <Button
        className="w-full"
        onClick={() => handleSave(user.id)}
        disabled={isLoading}
      >
        Сохранить
      </Button>
    )
  }
}

export { SaveSubscriptionsButton }
