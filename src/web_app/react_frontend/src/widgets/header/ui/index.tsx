import { Navigation } from '@/features/navigation'

export const Header = () => {
  return (
    <header className="sticky top-0 w-full inline-flex items-center shadow-md shadow-black/5 dark:bg-dark-blue bg-white backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:supports-[backdrop-filter]:bg-dark-blue/60 z-40 py-2">
      <Navigation />
      <div className="mx-auto inline-flex items-center">
        <h2 className="text-xl font-semibold uppercase tracking-tight">
          Brief
        </h2>
      </div>
    </header>
  )
}
