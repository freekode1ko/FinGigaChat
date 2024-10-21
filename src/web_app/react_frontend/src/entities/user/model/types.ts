type UserId = number

interface User {
  id: UserId
  first_name: string
  last_name?: string
  username?: string
  photo_url?: string
  auth_date: number
  hash: string
}

export type { User, UserId }
