import { Navigation } from '@/features/navigation'

export const Header = () => {
  return (
    <header className="sticky top-0 w-full inline-flex items-center bg-bg-color shadow-md shadow-black/5 z-40">
      <Navigation />
      <div className="mx-auto inline-flex items-center">
        <h2 className="text-xl font-semibold tracking-tight">WebApp Title</h2>
      </div>
    </header>
  )
}
