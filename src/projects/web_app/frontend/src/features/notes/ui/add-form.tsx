import { useForm } from 'react-hook-form'

import { useCreateNoteMutation } from '@/entities/notes'
import { selectUserData } from '@/entities/auth'
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
  mapCreateFormData,
  noteFormSchema,
} from '../model'

const AddNoteForm = ({ afterSubmit }: { afterSubmit: () => void }) => {
  const user = useAppSelector(selectUserData)
  const [trigger, { isLoading }] = useCreateNoteMutation()

  const noteForm = useForm<CreateNoteFormData>({
    resolver: zodResolver(noteFormSchema),
    defaultValues: getDefaultFormData(),
    disabled: isLoading,
  })
  const onSubmit = async (userId: number) => {
    await trigger(mapCreateFormData(noteForm.getValues(), userId)).unwrap()
    noteForm.reset()
    afterSubmit()
  }

  return (
    <Form {...noteForm}>
      <form
        onSubmit={noteForm.handleSubmit(() => onSubmit(user!.id))}
        className="space-y-4 w-full max-h-[400px] overflow-y-auto p-2"
      >
        <FormField
          control={noteForm.control}
          name="client"
          render={({ field }) => (
            <FormItem>
              <FormControl>
                <Input
                  variant="ghost"
                  fieldSize="lg"
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
                  variant="ghost"
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
          <Button onClick={afterSubmit} className="w-full" variant="outline">
            Отменить
          </Button>
        </div>
      </form>
    </Form>
  )
}

export { AddNoteForm }
