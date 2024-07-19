import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/shared/ui'

import { Quotes } from '../model'

export const QuotesTable = ({ data, params }: { data: Array<Quotes>, params: Array<string> }) => {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Название</TableHead>
          <TableHead className="text-right">Значение</TableHead>
          {params.map((param, paramIdx) => (
            <TableHead key={paramIdx} className="text-right">{param}</TableHead>
          ))}
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.map((item, itemIdx) => (
          <TableRow key={itemIdx}>
            <TableCell className="font-medium">{item.name}</TableCell>
            <TableCell className="text-right">
              {item.value ? item.value.toLocaleString() : 'N/A'}
            </TableCell>
            {item.params.map((param, paramIdx) => (
              <TableCell key={paramIdx} className="text-right">
                {param.value ? param.value.toLocaleString() : 'N/A'}
              </TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
