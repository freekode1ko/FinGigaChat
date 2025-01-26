import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import { sendMessageSchema } from '@/entities/bot'
import { cn, useStepper } from '@/shared/lib'
import { Button, Form } from '@/shared/ui'
import { zodResolver } from '@hookform/resolvers/zod'

import { ContentStep } from './content-step'
import { ReceiverStep } from './receivers-step'

const TOTAL_STEPS = 2

const getFieldsForStep = (step: number): Array<keyof z.infer<typeof sendMessageSchema>> => {
  switch (step) {
    case 1:
      return ['message']  // + 'files'
    case 2:
      return ['user_emails']
    default:
      return []
  }
}

export interface BaseMessageFormProps {
  onSuccess: () => void
  isLoading: boolean
  fieldValues: z.infer<typeof sendMessageSchema>
  onSubmit: (values: z.infer<typeof sendMessageSchema>) => Promise<unknown>
  loadingText: string
  successText: string
  errorText: string
}

const BaseMessageForm = ({ onSuccess, onSubmit, isLoading, fieldValues, loadingText, successText, errorText }: BaseMessageFormProps) => {
  const form = useForm<z.infer<typeof sendMessageSchema>>({
    resolver: zodResolver(sendMessageSchema),
    disabled: isLoading,
    defaultValues: fieldValues,
    reValidateMode: 'onChange',
    mode: 'onChange',
  })

  const baseOnSubmit = (values: z.infer<typeof sendMessageSchema>) => {
    toast.promise(onSubmit(values), {
      loading: loadingText,
      success: () => {
        form.reset()
        onSuccess()
        return successText
      },
      error: errorText,
    })
  }

  const { isFirstStep, isLastStep, handleNext, handlePrevious, currentStep, stepper } = useStepper({
    totalNumberOfSteps: TOTAL_STEPS,
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
      <div className="flex gap-4 flex-col md:flex-row md:gap-2 items-center md:justify-between">
        <div className='flex gap-2 items-center'>
          {Array.from({ length: TOTAL_STEPS }, (_, index) => (
            <div
              key={index}
              className={cn('w-3 h-3 rounded-full', index + 1 <= currentStep ? 'bg-accent' : 'bg-secondary')}
            />
          ))}
        </div>
        <div className='space-x-2'>
          {!isFirstStep &&
            <Button variant="outline" onClick={handlePrevious}>
              Назад
            </Button>
          }
          {isLastStep ? (
            <Button onClick={form.handleSubmit(baseOnSubmit)}>Отправить</Button>
          ) : (
            <Button
              type="button"
              onClick={handleNextForm}
            >
              Далее
            </Button>
          )}
        </div>
      </div>
    </form>
  </Form>
  )
}

export { BaseMessageForm }
