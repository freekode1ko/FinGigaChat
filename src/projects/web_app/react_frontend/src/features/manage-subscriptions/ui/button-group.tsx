import { ResetSubscriptionsButton } from './reset-button'
import { SaveSubscriptionsButton } from './save-button'

const ManageSubscriptionsButtonGroup = () => {
  return (
    <div className="sticky bottom-0 w-full rounded-lg inline-flex justify-between items-center shadow-md shadow-black/5 bg-background backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:supports-[backdrop-filter]:bg-dark-blue/60 z-50 py-2 px-4 gap-4">
      <SaveSubscriptionsButton />
      <ResetSubscriptionsButton />
    </div>
  )
}

export { ManageSubscriptionsButtonGroup }
