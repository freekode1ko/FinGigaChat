import { cva, type VariantProps } from 'class-variance-authority'
import React from 'react'

import { cn } from '../lib'

const badgeVariants = cva(
  'inline-flex items-center justify-center rounded-md border font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default:
          'border-transparent bg-foreground text-white',
        positive:
          'border-transparent bg-green-600 dark:bg-green-500 text-white hover:bg-green-600/80 dark:hover:bg-green-500/80',
        destructive:
          'border-transparent bg-destructive',
        outline: 'text-foreground',
      },
      size: {
        small: 'px-2.5 py-0.5 text-xs',
        default: 'px-3 py-1',
        large: 'px-4 py-1.5 text-lg',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, size, ...props }: BadgeProps) {
  return (
    <div
      className={cn(badgeVariants({ variant, size }), className)}
      {...props}
    />
  )
}

export { Badge }
