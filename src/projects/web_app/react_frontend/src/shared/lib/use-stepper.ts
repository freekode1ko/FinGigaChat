import { useEffect, useState } from 'react'

interface useStepperProps {
  totalNumberOfSteps?: number
  onStepChange?: (step: number) => void
  onStepsComplete?: () => void
  onStepsReset?: () => void
  onBack?: () => void
  stepperComponents?: Array<React.ReactNode>
}

/*
  Кастомный хук для работы со сложными компонентами, разбитыми на шаги.
  Шаг начинается с 1, и заканчивается на totalNumberOfSteps.
*/
export const useStepper = ({
  totalNumberOfSteps = 3,
  onStepChange,
  onStepsComplete,
  onStepsReset,
  onBack,
  stepperComponents,
}: useStepperProps) => {
  const [activeStep, setActiveStep] = useState(1)

  useEffect(() => {
    onStepChange && onStepChange(activeStep)
  }, [activeStep])

  const handleNext = () => {
    if (activeStep < totalNumberOfSteps) {
      setActiveStep(activeStep + 1)
    } else {
      onStepsComplete && onStepsComplete()
    }
  }

  const handlePrevious = () => {
    if (activeStep > 1) {
      setActiveStep(activeStep - 1)
    } else {
      onBack && onBack()
    }
  }

  const navigateStep = (step: number) => {
    if (step >= 1 && step <= totalNumberOfSteps) {
      setActiveStep(step)
    }
  }

  const handleReset = () => {
    setActiveStep(1)
    onStepsReset && onStepsReset()
  }

  const isFirstStep = activeStep === 1
  const isLastStep = activeStep === totalNumberOfSteps
  const currentStep = activeStep
  const stepper = stepperComponents && stepperComponents[currentStep - 1]

  return {
    isFirstStep,
    isLastStep,
    currentStep,
    handleNext,
    handlePrevious,
    navigateStep,
    handleReset,
    stepper,
  }
}
