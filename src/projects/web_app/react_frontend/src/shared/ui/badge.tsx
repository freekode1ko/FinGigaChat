import { cva, type VariantProps } from 'class-variance-authority'
import React from 'react'

import { cn } from '../lib'

const badgeVariants = cva(
  'inline-flex items-center justify-center rounded-full border font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default:
          'border-transparent bg-dark-blue dark:bg-white text-white dark:text-dark-blue hover:bg-dark-blue/80 dark:hover:bg-white/80',
        positive:
          'border-transparent bg-green-600 dark:bg-green-500 text-white hover:bg-green-600/80 dark:hover:bg-green-500/80',
        destructive:
          'border-transparent bg-red-600 dark:bg-red-500 text-white hover:bg-red-600/80 dark:hover:bg-red-500/80',
        outline: 'text-dark-blue dark:text-white',
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
