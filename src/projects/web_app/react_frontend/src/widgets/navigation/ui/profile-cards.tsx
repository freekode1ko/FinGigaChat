import { Link } from 'react-router-dom'

import { Card, CardTitle } from '@/shared/ui'

import { type MenuItem, profileItems } from '../model'

const MenuItemLink = ({ item }: { item: MenuItem }) => (
  <Link to={item.path} className='block'>
    <Card className='relative border border-border bg-secondary hover:bg-background min-h-32 p-4'>
      <CardTitle>{item.name}</CardTitle>
      <item.icon className='absolute right-4 bottom-4 h-16 w-16 text-muted opacity-20' />
    </Card>
  </Link>
)


/*
  Компонент с навигационными кнопками в профиле пользователя.
  Предназначен для навигации по закрытым разделам, которые
  доступны только авторизованным пользователям. 
*/
export const ProfileNavigation = () => {
  return (
    <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
      {profileItems.map((item) => (
        <MenuItemLink key={item.path} item={item} />
      ))}
    </div>
  )
}
