import { cva, type VariantProps } from 'class-variance-authority'
import React from 'react'

import { cn } from '../lib'

const inputVariants = cva(
  'block w-full rounded-md bg-transparent ring-offset-secondary-100 dark:ring-offset-secondary-600 file:border-0 file:bg-transparent file:text-sm file:font-medium dark:[color-scheme:dark] placeholder:text-secondary-200 dark:placeholder:text-secondary-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'border border-secondary-100 dark:border-secondary-600',
        ghost: 'border-none',
      },
      fieldSize: {
        default: 'h-10 px-3 py-2 text-sm',
        lg: 'h-14 px-4 py-2 text-lg',
      },
    },
    defaultVariants: {
      variant: 'default',
      fieldSize: 'default',
    },
  }
)

interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement>,
    VariantProps<typeof inputVariants> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, variant, fieldSize, type, ...props }, ref) => {
    return (
      <input
        className={cn(inputVariants({ variant, fieldSize, className }))}
        type={type}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = 'Input'

export { Input }
