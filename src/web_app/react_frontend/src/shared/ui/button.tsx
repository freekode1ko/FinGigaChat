import { cva, type VariantProps } from 'class-variance-authority'
import React from 'react'

import { cn } from '../lib'

const buttonVariants = cva(
  'rounded-lg disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'text-white bg-primary-500 hover:bg-primary-600',
        secondary: 'text-secondary-700 bg-secondary-100 hover:bg-secondary-200',
      },
      size: {
        default: 'px-4 py-2',
        large: 'px-4 py-4',
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
  mobileFull?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, mobileFull = false, ...props }, ref) => {
    return (
      <button
        className={cn(
          buttonVariants({ variant, size, className }),
          mobileFull && 'w-full md:w-fit'
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = 'Button'

export { Button }
