import type { VariantProps } from 'class-variance-authority'

import { inputVariants } from './variants'

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement>,
    VariantProps<typeof inputVariants> {}
