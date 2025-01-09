import React from 'react'

import { cn } from '../lib'

export interface StepProps extends React.HTMLAttributes<HTMLDivElement> {
  active: boolean
}

const Step = React.forwardRef<HTMLDivElement, StepProps>(
  ({ className, active, ...props }, ref) => {
    return (
      <div
        className={cn(
          active ? 'bg-primary' : 'bg-secondary',
          'mx-auto my-4 h-2 w-full rounded-full',
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Step.displayName = 'Step'

export { Step }
