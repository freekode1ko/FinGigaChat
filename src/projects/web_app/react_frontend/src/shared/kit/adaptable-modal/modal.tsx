import { useMediaQuery } from '@/shared/lib'
import { DESKTOP_MEDIA_QUERY } from '@/shared/model'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from '@/shared/ui'

interface AdaptableModalProps extends React.PropsWithChildren {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  title?: string
  description?: string
  className?: string
  trigger?: React.ReactNode
  bottomSlot?: React.ReactNode
}

export const AdaptableModal = ({
  open,
  onOpenChange,
  title,
  description,
  children,
  className,
  trigger,
  bottomSlot,
}: AdaptableModalProps) => {
  const isDesktop = useMediaQuery(DESKTOP_MEDIA_QUERY)

  if (isDesktop) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        {trigger && <DialogTrigger asChild>{trigger}</DialogTrigger>}
        <DialogContent className={className}>
          <DialogHeader>
            {title && <DialogTitle>{title}</DialogTitle>}
            {description && (
              <DialogDescription>{description}</DialogDescription>
            )}
          </DialogHeader>
          {children}
          {bottomSlot && <DialogFooter>{bottomSlot}</DialogFooter>}
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      {trigger && <DrawerTrigger asChild>{trigger}</DrawerTrigger>}
      <DrawerContent className={className}>
        <div className="mx-auto w-full max-w-sm max-h-64 overflow-y-auto md:max-h-full">
          <DrawerHeader>
            {title && <DrawerTitle>{title}</DrawerTitle>}
            {description && (
              <DrawerDescription>{description}</DrawerDescription>
            )}
          </DrawerHeader>
          <div className="p-4">{children}</div>
          {bottomSlot && <DrawerFooter>{bottomSlot}</DrawerFooter>}
        </div>
      </DrawerContent>
    </Drawer>
  )
}
