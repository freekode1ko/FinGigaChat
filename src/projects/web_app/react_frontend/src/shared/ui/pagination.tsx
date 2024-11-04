import React from 'react'

interface ShowMoreButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {}

const ShowMoreButton = React.forwardRef<HTMLButtonElement, ShowMoreButtonProps>(
  ({ ...props }, ref) => {
    return (
      <button
        className="w-full h-16 bg-secondary-100 dark:bg-transparent hover:bg-secondary-300 dark:hover:bg-secondary-600 text-dark-blue dark:text-white text-center"
        ref={ref}
        {...props}
      >
        Показать больше
      </button>
    )
  }
)
ShowMoreButton.displayName = 'ShowMoreButton'

export { ShowMoreButton }
