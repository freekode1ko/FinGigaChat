import { cva, type VariantProps } from 'class-variance-authority'
import React from 'react'

import { Slot } from '@radix-ui/react-slot'

import { cn } from '../lib'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 rounded-md whitespace-nowrap text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary-800 dark:bg-primary-400 text-white',
        secondary: 'bg-secondary-300 dark:bg-secondary-800 text-white',
        destructive: 'bg-red-200 dark:bg-red-500 hover:bg-red-200/90 dark:hover:bg-red-500/90',
        outline:
          'border text-dark-blue dark:text-white border-dark-blue dark:border-white transparent hover:bg-secondary-100 dark:hover:bg-secondary-600',
        ghost:
          'text-dark-blue dark:text-white transparent hover:bg-secondary-100 dark:hover:bg-secondary-600',
      },
      size: {
        default: 'h-10 px-4 py-2',
        icon: 'h-10 w-10',
        sm: 'h-9 px-3',
        lg: 'h-11 px-8',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button'
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = 'Button'

export { Button }
