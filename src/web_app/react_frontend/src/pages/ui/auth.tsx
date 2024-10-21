import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { AuthFormStep1, AuthFormStep2 } from '@/features/user'
import { SITE_MAP } from '@/shared/model'
import { Step, TypographyH2 } from '@/shared/ui'

const AuthPage = () => {
  const navigate = useNavigate()
  const [step, setStep] = useState<1 | 2>(1)
  return (
    <div className="py-8 px-6">
      <div className="flex flex-col justify-center items-center space-y-4 mx-auto lg:max-w-screen-sm">
        <TypographyH2>Авторизация</TypographyH2>
        <div className="flex flex-nowrap w-full gap-2 mb-4">
          <Step active={step > 0} />
          <Step active={step > 1} />
        </div>
        {step === 1 && <AuthFormStep1 onSuccessNavigate={() => setStep(2)} />}
        {step === 2 && (
          <AuthFormStep2
            onSuccessNavigate={() => navigate(SITE_MAP.dashboard)}
          />
        )}
      </div>
    </div>
  )
}

export { AuthPage }
