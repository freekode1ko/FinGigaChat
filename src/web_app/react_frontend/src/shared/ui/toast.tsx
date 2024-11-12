import { CircleAlert, CircleCheck } from 'lucide-react'
import { Toaster as Sonner } from 'sonner'

type ToasterProps = React.ComponentProps<typeof Sonner>

const Toaster = ({ ...props }: ToasterProps) => {
  return (
    <Sonner
      className="toaster group"
      icons={{
        error: <CircleAlert className="font-semibold text-destructive" />,
        success: <CircleCheck className="font-semibold text-accent" />,
      }}
      toastOptions={{
        classNames: {
          toast:
            'group toast group-[.toaster]:bg-background border border-border group-[.toaster]:text-text group-[.toaster]:shadow-lg gap-4',
          description:
            'group-[.toast]:text-muted-foreground',
          actionButton:
            'group-[.toast]:bg-primary group-[.toast]:text-primary-foreground',
          cancelButton:
            'group-[.toast]:text-muted-foreground',
          success: 'border-accent',
          error: 'border-destructive',
        },
      }}
      {...props}
    />
  )
}

export { Toaster }
