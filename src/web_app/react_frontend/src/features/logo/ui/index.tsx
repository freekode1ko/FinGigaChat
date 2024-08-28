import { Link } from 'react-router-dom'

import { TypographyH2 } from '@/shared/ui'

interface LogoProps {
  navigateOnClick?: boolean
}

const Logo = () => {
  return (
    <div className="inline-flex items-center">
      <TypographyH2 className="uppercase">Brief</TypographyH2>
    </div>
  )
}

const LogoWrapper = ({ navigateOnClick }: LogoProps) => {
  if (navigateOnClick) {
    return (
      <Link to="/">
        <Logo />
      </Link>
    )
  }
  return <Logo />
}

export { LogoWrapper as Logo }
