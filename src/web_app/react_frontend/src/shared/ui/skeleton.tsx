import { cn } from '../lib'

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn('animate-pulse rounded-lg bg-hint-color', className)}
      {...props}
    />
  )
}

export { Skeleton }
