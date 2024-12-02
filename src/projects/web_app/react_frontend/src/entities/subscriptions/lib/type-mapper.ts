interface SubscriptionMap {
  title: string
  link: string
}

export const mapSubscriptionType = (type: string): SubscriptionMap => {
  switch (type) {
    case 'clients':
      return {
        title: 'Клиенты',
        link: '/clients',
      }
    default:
      return {
        title: 'Клиенты',
        link: '/clients',
      }
  }
}
