import { cva, type VariantProps } from 'class-variance-authority'
import React from 'react'

import { cn } from '../lib'

const textareaVariants = cva(
  'flex min-h-[80px] w-full rounded-md bg-transparent px-3 py-2 text-sm ring-offset-secondary-100 dark:ring-offset-secondary-600 dark:[color-scheme:dark] placeholder:text-secondary-200 dark:placeholder:text-secondary-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'border border-secondary-100 dark:border-secondary-600',
        ghost: 'border-none',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement>,
    VariantProps<typeof textareaVariants> {}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, variant, ...props }, ref) => {
    return (
      <textarea
        className={cn(textareaVariants({ variant, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Textarea.displayName = 'Textarea'

export { Textarea }
