import React from 'react'

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
  Button,
} from '@/shared/ui'

interface ActionItem {
  report_name: string
  report_id: number
}

interface MenuItem {
  name: string
  analytics_menu_id: number
  nearest_menu: MenuItem[]
  actions?: ActionItem[]
}

const RecursiveAccordion: React.FC<{ menuItems: MenuItem[] }> = ({
  menuItems,
}) => {
  const handleActionClick = (report_id: number) => {
    console.log(`Requesting report with ID: ${report_id}`)
  }

  return (
    <Accordion type="single" collapsible className="ml-2">
      {menuItems.map((item) => (
        <AccordionItem
          key={item.analytics_menu_id}
          value={String(item.analytics_menu_id)}
        >
          <AccordionTrigger>{item.name}</AccordionTrigger>
          {item.nearest_menu.length > 0 && (
            <AccordionContent>
              <RecursiveAccordion menuItems={item.nearest_menu} />
            </AccordionContent>
          )}
          {item.actions && item.actions.length > 0 && (
            <AccordionContent>
              <div className="flex flex-col space-y-2">
                {item.actions.map((action) => (
                  <Button
                    key={action.report_id}
                    onClick={() => handleActionClick(action.report_id)}
                  >
                    {action.report_name}
                  </Button>
                ))}
              </div>
            </AccordionContent>
          )}
        </AccordionItem>
      ))}
    </Accordion>
  )
}

const mockMenuData: MenuItem = {
  name: 'Аналитика публичных рынков',
  analytics_menu_id: 1,
  nearest_menu: [
    {
      name: 'Отрасли',
      analytics_menu_id: 2,
      nearest_menu: [
        {
          name: 'Энергетика',
          analytics_menu_id: 3,
          nearest_menu: [
            {
              name: 'Нефть и газ',
              analytics_menu_id: 4,
              nearest_menu: [],
              actions: [
                { report_name: 'Отчет за 1 день', report_id: 101 },
                { report_name: 'Отчет за 1 месяц', report_id: 102 },
              ],
            },
            {
              name: 'Возобновляемая энергия',
              analytics_menu_id: 5,
              nearest_menu: [
                {
                  name: 'Солнечная энергия',
                  analytics_menu_id: 6,
                  nearest_menu: [],
                  actions: [
                    { report_name: 'Отчет за 1 месяц', report_id: 103 },
                  ],
                },
                {
                  name: 'Ветроэнергетика',
                  analytics_menu_id: 7,
                  nearest_menu: [],
                  actions: [{ report_name: 'Отчет за 1 день', report_id: 104 }],
                },
              ],
            },
          ],
        },
        {
          name: 'Финансы',
          analytics_menu_id: 8,
          nearest_menu: [],
          actions: [{ report_name: 'Отчет по финансам', report_id: 105 }],
        },
      ],
    },
    {
      name: 'Рынки',
      analytics_menu_id: 9,
      nearest_menu: [
        {
          name: 'Фондовые рынки',
          analytics_menu_id: 10,
          nearest_menu: [],
          actions: [
            { report_name: 'Отчет по фондовым рынкам', report_id: 106 },
          ],
        },
        {
          name: 'Валютные рынки',
          analytics_menu_id: 11,
          nearest_menu: [],
          actions: [
            { report_name: 'Отчет по валютным рынкам', report_id: 107 },
          ],
        },
      ],
    },
  ],
}

const AnalyticsPage = () => {
  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">{mockMenuData.name}</h1>
      <RecursiveAccordion menuItems={mockMenuData.nearest_menu} />
    </div>
  )
}

export { AnalyticsPage }
