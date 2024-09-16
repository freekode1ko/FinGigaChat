import React from 'react'

import { cn } from '../lib'

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => {
    return (
      <textarea
        className={cn(
          'flex min-h-[80px] w-full rounded-md border border-secondary-100 dark:border-secondary-600 bg-transparent px-3 py-2 text-sm ring-offset-secondary-100 dark:ring-offset-secondary-600 dark:[color-scheme:dark] placeholder:text-secondary-200 dark:placeholder:text-secondary-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Textarea.displayName = 'Textarea'

export { Textarea }
