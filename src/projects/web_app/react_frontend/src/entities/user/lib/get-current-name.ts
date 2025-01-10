import type { User } from '../model'

/*
  Возвращает имя пользователя или его email.
*/
const getCurrentName = (user: User) => {
  if (user.full_name && user.full_name.trim().length > 0) return user.full_name
  return user.email
}

export { getCurrentName }
