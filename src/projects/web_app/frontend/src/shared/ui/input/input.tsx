import React from 'react'

import { cn } from '@/shared/lib'

import type { InputProps } from './types'
import { inputVariants } from './variants'

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
