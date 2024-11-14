import { Link } from 'react-router-dom'

import { TypographyH2 } from '@/shared/ui'

interface LogoProps {
  navigateOnClick?: boolean
}

const Logo = () => {
  return (
    <TypographyH2 className="uppercase">Brief</TypographyH2>
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
