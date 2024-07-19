import { Navigation } from '@/features/navigation'

export const Header = () => {
  return (
    <header className="sticky top-0 w-full bg-bg-color shadow-md shadow-secondary-bg-color/5 z-10">
      <Navigation />
    </header>
  )
}
