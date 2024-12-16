import type { LucideIcon } from 'lucide-react'
import React from 'react'

import { cn } from '@/shared/lib'
import type { InputProps } from '@/shared/ui/input'
import { inputVariants } from '@/shared/ui/input'

interface IconInputProps extends InputProps {
  Icon: LucideIcon
}

const IconInput = React.forwardRef<HTMLInputElement, IconInputProps>(
  ({ Icon, className, variant, fieldSize, type, ...props }, ref) => {
    return (
      <div className="relative flex items-center">
        <Icon className="absolute left-3 h-5 w-5 text-muted-foreground pointer-events-none" />
        <input
          className={cn(
            inputVariants({ variant, fieldSize, className }),
            'pl-10'
          )}
          type={type}
          ref={ref}
          {...props}
        />
      </div>
    )
  }
)
IconInput.displayName = 'IconInput'

export { IconInput }
