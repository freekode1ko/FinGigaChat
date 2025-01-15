import { cva } from 'class-variance-authority'

export const inputVariants = cva(
  'block w-full rounded-md bg-transparent ring-offset-secondary file:border-0 file:bg-transparent file:text-sm file:font-medium dark:[color-scheme:dark] placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'border border-input',
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
