import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { ConfirmationCodeStep, EmailStep } from '@/features/auth'
import { SITE_MAP } from '@/shared/model'
import { Step, TypographyH2 } from '@/shared/ui'

const AuthPage = () => {
  const navigate = useNavigate()
  const [step, setStep] = useState<number>(1)
  const [regEmail, setRegEmail] = useState<string>('') // temp
  return (
    <div className="py-8">
      <div className="flex flex-col justify-center items-center space-y-4 mx-auto px-4 lg:max-w-screen-sm">
        <TypographyH2>Авторизация</TypographyH2>
        <div className="flex flex-nowrap w-full gap-2 mb-4">
          <Step active={step > 0} />
          <Step active={step > 1} />
        </div>
        {step === 1 && (
          <EmailStep
            onEmailChange={setRegEmail}
            onSuccessNavigate={() => setStep(2)}
          />
        )}
        {step === 2 && (
          <ConfirmationCodeStep
            forEmail={regEmail}
            onSuccessNavigate={() => navigate(SITE_MAP.dashboard)}
          />
        )}
      </div>
    </div>
  )
}

export { AuthPage }
