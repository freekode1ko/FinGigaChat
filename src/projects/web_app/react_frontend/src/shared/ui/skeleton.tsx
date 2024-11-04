import { cn } from '../lib'

const Skeleton = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => {
  return (
    <div
      className={cn(
        'animate-pulse rounded-lg bg-secondary-300 dark:bg-secondary-800',
        className
      )}
      {...props}
    />
  )
}

export { Skeleton }
