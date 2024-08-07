import { Link } from 'react-router-dom'

import { TypographyH2 } from '@/shared/ui'

const Logo = () => {
  return (
    <Link to="/">
      <div className="inline-flex items-center">
        <TypographyH2 className="uppercase">Brief</TypographyH2>
      </div>
    </Link>
  )
}

export { Logo }
