type UserId = number

interface User {
  email: string
  role: number
  username?: string
  full_name?: string
}

interface UserRole {
  id: number
  name: string
  description: string
}

export type { User, UserId, UserRole }
