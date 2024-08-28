import React from 'react'

import {
  Button,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/shared/ui'

import { Quotes } from '../model'

interface QuotesTableProps extends React.PropsWithChildren {
  headParams: Array<string>
}

const QuotesTableRow = ({
  quote,
  priceChart,
  onRowClick,
}: {
  quote: Quotes
  onRowClick: () => void
  priceChart?: React.ReactNode
}) => {
  return (
    <TableRow>
      <TableCell className="cursor-pointer font-medium">
        <Button variant="ghost" onClick={onRowClick} asChild>
          <span className="inline-flex items-center gap-2">
            <img
              src={quote.image_path}
              alt={`${quote.name} image`}
              className="h-4 w-4"
            />
            {quote.name}
          </span>
        </Button>
      </TableCell>
      <TableCell className="text-right">
        {quote.value ? quote.value.toLocaleString() : 'N/A'}
      </TableCell>
      {quote.params.map((param, paramIdx) => (
        <TableCell key={paramIdx} className="text-right">
          {param.value ? param.value.toLocaleString() : 'N/A'}
        </TableCell>
      ))}
      <TableCell className="text-right">{priceChart || 'N/A'}</TableCell>
    </TableRow>
  )
}

const QuotesTable = ({ children, headParams }: QuotesTableProps) => {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Название</TableHead>
          <TableHead className="text-right">Значение</TableHead>
          {headParams.map((param, paramIdx) => (
            <TableHead key={paramIdx} className="text-right">
              {param}
            </TableHead>
          ))}
          <TableHead className="text-right">График</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>{children}</TableBody>
    </Table>
  )
}

export { QuotesTable, QuotesTableRow }
