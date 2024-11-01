import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { useMediaQuery } from '@/shared/lib'
import { Button, Paragraph, Step, TypographyH2 } from '@/shared/ui'

const WelcomePage = () => {
  const isDesktop = useMediaQuery('(min-width: 768px)')
  const navigate = useNavigate()
  const [step, setStep] = useState<number>(1)

  useEffect(() => {
    const beenHere = localStorage.getItem('onboarding')
    if (beenHere || isDesktop) {
      navigate('/news')
    }
  })

  const handleNextStep = () => {
    if (step < 3) {
      setStep(step + 1)
    } else {
      localStorage.setItem('onboarding', 'true')
      navigate('/news')
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-4">
      <div className="flex w-full justify-center space-x-2">
        <Step active={step > 0} />
        <Step active={step > 1} />
        <Step active={step > 2} />
      </div>

      <div className="flex-1 flex flex-col items-center justify-center text-center">
        {step === 1 && (
          <SliderContent title='Дашборд'>
            Создавайте свой персональный дашборд, настройте его под свои задачи и следите за интересующими вас котировками!
          </SliderContent>
        )}
        {step === 2 && (
          <SliderContent title='Новости'>
            Получайте актуальные новости и обновления по вашим финансовым инструментам, чтобы оставаться в курсе каждый день!
          </SliderContent>
        )}
        {step === 3 && (
          <SliderContent title='Заметки и встречи'>
            Планируйте встречи, создавайте заметки и контролируйте время для достижения целей, чтобы ничего не пропустить!
          </SliderContent>
        )}
      </div>

      <Button size='lg' className='w-full' onClick={handleNextStep}>
        {step < 3 ? 'Далее' : 'В приложение!'}
      </Button>
    </div>
  )
}

const SliderContent = ({title, children}: {title: string} & React.PropsWithChildren) => {
  return (
    <div className="w-full">
      <div className="h-80 w-3/4 bg-gray-400 mx-auto rounded-md"></div>
      <TypographyH2 className="mt-6">{title}</TypographyH2>
      <Paragraph className="mt-4">{children}</Paragraph>
    </div>
  )
}

export { WelcomePage }
