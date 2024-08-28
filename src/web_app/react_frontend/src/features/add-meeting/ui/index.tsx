import { Plus } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { useCreateMeetingMutation } from '@/entities/meetings'
import { type UserId } from '@/entities/user'
import {
  Button,
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  Input,
} from '@/shared/ui'
import { zodResolver } from '@hookform/resolvers/zod'

import { getDefaultDates } from '../lib'
import { meetingFormSchema } from '../model'

interface AddMeetingButtonProps {
  userId: UserId
}

const AddMeetingButton = ({userId}: AddMeetingButtonProps) => {
  const [isOpen, setIsOpen] = useState<boolean>(false)
  const [trigger, { isLoading, isError }] = useCreateMeetingMutation()
  const handleFormSubmit = async () => {
    const formValues = meetingForm.getValues()
    await trigger({
      user_id: userId,
      ...formValues,
      timezone: parseInt(formValues.timezone),
      date_start: new Date(formValues.date_start).toISOString(),
      date_end: new Date(formValues.date_end).toISOString(),
    }).unwrap()
    setIsOpen(false)
  }

  const [startDate, endDate] = getDefaultDates()

  const meetingForm = useForm<z.infer<typeof meetingFormSchema>>({
    resolver: zodResolver(meetingFormSchema),
    defaultValues: {
      date_start: startDate,
      date_end: endDate,
      theme: '',
      description: '',
      timezone: '',
    },
  })
  return (
    <Drawer open={isOpen} onOpenChange={setIsOpen}>
      <DrawerTrigger asChild>
        <Button variant="ghost" size="icon">
          <Plus />
        </Button>
      </DrawerTrigger>
      <DrawerContent>
        <div className="mx-auto w-full max-w-sm">
          <DrawerHeader>
            <DrawerTitle>Создать встречу</DrawerTitle>
            <DrawerDescription>
              Вы можете добавить встречу в свой календарь
            </DrawerDescription>
          </DrawerHeader>
          <Form {...meetingForm}>
            <form
              onSubmit={meetingForm.handleSubmit(handleFormSubmit)}
              className="space-y-4 w-full max-h-[400px] overflow-y-auto p-2"
            >
              <FormField
                control={meetingForm.control}
                name="theme"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Тема встречи</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Обсуждение текущих задач"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={meetingForm.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Краткое описание</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Встреча с Иваном Ивановым для обсуждения текущих задач"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={meetingForm.control}
                name="date_start"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Начало</FormLabel>
                    <FormControl>
                      <Input type="datetime-local" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={meetingForm.control}
                name="date_end"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Конец</FormLabel>
                    <FormControl>
                      <Input type="datetime-local" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={meetingForm.control}
                name="timezone"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Временная зона</FormLabel>
                    <FormControl>
                      <Input
                        type='number'
                        placeholder="3"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="flex gap-2">
                <Button variant={isError ? 'destructive' : 'default'} type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? 'Сохраняем...' : isError ? 'Попробовать еще раз' : 'Сохранить'}
                </Button>
                <DrawerClose asChild>
                  <Button variant="outline" className="w-full">
                    Отменить
                  </Button>
                </DrawerClose>
              </div>
            </form>
          </Form>
        </div>
      </DrawerContent>
    </Drawer>
  )
}

export { AddMeetingButton }
