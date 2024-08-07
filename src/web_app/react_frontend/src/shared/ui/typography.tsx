import { cn } from '../lib'

interface TypographyHeadProps
  extends React.BaseHTMLAttributes<HTMLHeadElement> {}

interface TypographyParagraphProps
  extends React.BaseHTMLAttributes<HTMLParagraphElement> {}

const TypographyH1 = ({ className, ...props }: TypographyHeadProps) => {
  return (
    <h1
      className={cn(
        className,
        'scroll-m-20 text-4xl font-extrabold tracking-tight'
      )}
      {...props}
    />
  )
}

const TypographyH2 = ({ className, ...props }: TypographyHeadProps) => {
  return (
    <h2
      className={cn(
        className,
        'scroll-m-20 text-2xl font-semibold tracking-tight first:mt-0'
      )}
      {...props}
    />
  )
}

const Paragraph = ({ className, ...props }: TypographyParagraphProps) => {
  return (
    <p
      className={cn(className, 'leading-7 [&:not(:first-child)]:mt-6')}
      {...props}
    />
  )
}

export { Paragraph, TypographyH1, TypographyH2 }
