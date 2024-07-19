import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/shared/ui'

import { Quotes } from '../model'

export const QuotesTable = ({ data }: { data: Array<Quotes> }) => {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Название</TableHead>
          <TableHead>Значение</TableHead>
          <TableHead className="text-right">%день</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.map((item, itemIdx) => (
          <TableRow key={itemIdx}>
            <TableCell className="font-medium">{item.name}</TableCell>
            <TableCell>
              {item.value ? item.value.toLocaleString() : '0.00'}
            </TableCell>
            <TableCell className="text-right">
              {item.params.map((param, paramIdx) => (
                <p key={paramIdx}>
                  {param.value ? param.value.toLocaleString() : '—'}
                </p>
              ))}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
