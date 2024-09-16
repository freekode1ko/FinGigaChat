import { SquarePen } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'

import { useCreateNoteMutation } from '@/entities/notes'
import { selectUserData } from '@/entities/user'
import { useAppSelector } from '@/shared/lib'
import {
  Button,
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
  Input,
  Textarea,
} from '@/shared/ui'
import { zodResolver } from '@hookform/resolvers/zod'

import {
  type CreateNoteFormData,
  getDefaultFormData,
  mapFormData,
  noteFormSchema,
} from '../model'

/*
 * Кнопка для добавления заметки. При нажатии в том же месте появляется форма.
 * Возвращается к исходному виду при успешной отправке.
 */
const AddNoteButton = () => {
  const user = useAppSelector(selectUserData)
  const [isFormOpened, setIsFormOpened] = useState<boolean>(false)
  const [trigger, { isLoading }] = useCreateNoteMutation()

  const noteForm = useForm<CreateNoteFormData>({
    resolver: zodResolver(noteFormSchema),
    defaultValues: getDefaultFormData(),
    disabled: isLoading,
  })
  const onSubmit = async (userId: number) => {
    await trigger(mapFormData(noteForm.getValues(), userId)).unwrap()
    noteForm.reset()
    setIsFormOpened(false)
  }

  if (user) {
    return (
      <>
        {isFormOpened ? (
          <Form {...noteForm}>
            <form
              onSubmit={noteForm.handleSubmit(() => onSubmit(user.userId))}
              className="space-y-4 w-full max-h-[400px] overflow-y-auto p-2"
            >
              <FormField
                control={noteForm.control}
                name="client"
                render={({ field }) => (
                  <FormItem>
                    <FormControl>
                      <Input
                        placeholder="Введите название заметки..."
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={noteForm.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormControl>
                      <Textarea
                        placeholder="Введите текст заметки..."
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="flex gap-2">
                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? 'Сохраняем...' : 'Сохранить'}
                </Button>
                <Button
                  onClick={() => setIsFormOpened(false)}
                  className="w-full"
                  variant="outline"
                >
                  Отменить
                </Button>
              </div>
            </form>
          </Form>
        ) : (
          <Button onClick={() => setIsFormOpened(true)} variant="ghost">
            <SquarePen /> Добавить заметку
          </Button>
        )}
      </>
    )
  }
}

export { AddNoteButton }
