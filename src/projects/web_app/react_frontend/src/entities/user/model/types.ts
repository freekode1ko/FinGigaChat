type UserId = number

interface User {
  id: UserId
  email: string
  role: number
  username?: string
  full_name?: string
}

export type { User, UserId }
