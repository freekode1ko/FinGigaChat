import { cva, type VariantProps } from 'class-variance-authority'
import React from 'react'

import { Slot } from '@radix-ui/react-slot'

import { cn } from '../lib'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 rounded-md whitespace-nowrap text-sm font-medium transition-colors disabled:pointer-events-none disabled:opacity-50 cursor-pointer',
  {
    variants: {
      variant: {
        default: 'bg-primary text-white hover:opacity-90',
        secondary: 'bg-secondary hover:bg-background border border-border',
        destructive: 'bg-destructive text-destructive-foreground hover:opacity-90',
        outline: 'border border-border transparent hover:bg-secondary',
        ghost: 'transparent hover:bg-secondary',
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
        className={cn(buttonVariants({ className, variant, size }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = 'Button'

export { Button }
