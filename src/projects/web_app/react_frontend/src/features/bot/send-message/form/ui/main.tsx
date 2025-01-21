import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import { sendMessageSchema, useSendMessageMutation } from '@/entities/bot'
import { useStepper } from '@/shared/lib'
import { Button, Form } from '@/shared/ui'
import { zodResolver } from '@hookform/resolvers/zod'

import { ContentStep } from './content-step'
import { ReceiverStep } from './receivers-step'

const getFieldsForStep = (step: number): Array<keyof z.infer<typeof sendMessageSchema>> => {
  switch (step) {
    case 1:
      return ['message', 'files']
    case 2:
      return ['user_emails']
    default:
      return []
  }
}

const SendMessageForm = ({ onSuccess }: { onSuccess: () => void }) => {
  const [send, { isLoading }] = useSendMessageMutation()

  const form = useForm<z.infer<typeof sendMessageSchema>>({
    resolver: zodResolver(sendMessageSchema),
    disabled: isLoading,
    defaultValues: {
      message: '',
      user_emails: [],
      files: [],
    },
    reValidateMode: 'onChange',
    mode: 'onChange',
  })

  const onSubmit = (values: z.infer<typeof sendMessageSchema>) => {
    toast.promise(send(values), {
      loading: 'Запускаем рассылку...',
      success: () => {
        form.reset()
        onSuccess()
        return 'Рассылка успешно запущена!'
      },
      error: 'Ошибка при запуске рассылки',
    })
  }

  const { isFirstStep, isLastStep, handleNext, handlePrevious, currentStep, stepper } = useStepper({
    totalNumberOfSteps: 2,
    stepperComponents: [<ContentStep key={1} />, <ReceiverStep key={2} />],
  })

  const fieldsToValidate = getFieldsForStep(currentStep)

  const handleNextForm = async () => {
    const isValid = await form.trigger(fieldsToValidate)
    if (isValid) handleNext()
  }

  return (
  <Form {...form}>
    <form onSubmit={(e) => e.preventDefault()} className="space-y-4">
      {stepper}
      <div className="flex gap-4 flex-col md:flex-row md:gap-2 md:justify-end">
        {!isFirstStep &&
          <Button variant="outline" onClick={handlePrevious}>
            Назад
          </Button>
        }
        {isLastStep ? (
          <Button onClick={form.handleSubmit(onSubmit)}>Отправить</Button>
        ) : (
          <Button
            type="button"
            onClick={handleNextForm}
          >
            Далее
          </Button>
        )}
      </div>
    </form>
  </Form>
  )
}

export { SendMessageForm }
