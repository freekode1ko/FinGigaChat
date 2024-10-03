import { useNavigate } from 'react-router-dom'

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
  Button,
} from '@/shared/ui'

import type { Menu } from '../model'

interface AnalyticsAccordionProps {
  menuItems: Array<Menu>
}

const AnalyticsAccordion = ({ menuItems }: AnalyticsAccordionProps) => {
  const navigate = useNavigate()
  return (
    <>
      {menuItems.map((item, itemIdx) => (
        <>
          {item.nearest_menu.length > 0 ? (
            <Accordion type="single" collapsible className="ml-2">
              <AccordionItem key={itemIdx} value={item.title}>
                <AccordionTrigger>{item.title}</AccordionTrigger>
                <AccordionContent>
                  <AnalyticsAccordion menuItems={item.nearest_menu} />
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          ) : (
            <Button
              onClick={() => navigate(`/analytics/${item.analytics_menu_id}`)}
              className="whitespace-normal text-left [&:not(:last-child)]:mb-4"
            >
              {item.title}
            </Button>
          )}
        </>
      ))}
    </>
  )
}

export { AnalyticsAccordion }
