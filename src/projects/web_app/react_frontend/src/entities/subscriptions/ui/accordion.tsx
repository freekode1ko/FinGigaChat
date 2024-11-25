import React from 'react'

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/shared/ui'

import type { Subscription } from '../model'

interface SubscriptionsAccordionProps extends React.PropsWithChildren {
  subscription: Subscription
}

const SubscriptionsAccordion = ({
  subscription,
  children,
}: SubscriptionsAccordionProps) => {
  return (
    <Accordion
      type="single"
      collapsible
      className="ml-2"
      key={subscription.subscription_id}
    >
      <AccordionItem
        key={subscription.subscription_id}
        value={subscription.name}
      >
        <AccordionTrigger>{subscription.name}</AccordionTrigger>
        <AccordionContent>{children}</AccordionContent>
      </AccordionItem>
    </Accordion>
  )
}

export { SubscriptionsAccordion }
