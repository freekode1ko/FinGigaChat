import { CloudUpload, Paperclip } from 'lucide-react'

import {
  FileInput,
  FileUploader,
  FileUploaderContent,
  FileUploaderItem,
  type FileUploaderProps,
} from '../ui/file-upload'

interface FileFieldProps extends FileUploaderProps {
  helpText?: string
  orientation?: 'vertical' | 'horizontal'
}

const getFilename = (filename: string) => {
  if (filename.length > 20) {
    return filename.slice(0, 20) + '...' 
  }
  return filename
}

const FileUploadField = ({ helpText, orientation = 'vertical', ...props }: FileFieldProps) => {
  return (
    <FileUploader {...props} className="relative bg-background rounded-lg p-2" orientation={orientation}>
      <FileInput
        id="fileInput"
        className="outline-dashed outline-1 outline-slate-500"
      >
        <div className="flex items-center justify-center flex-col p-8 w-full ">
          <CloudUpload className="text-muted w-10 h-10" />
          <p className="mb-1 text-sm text-muted text-center">
            <span className="font-semibold">Кликните для загрузки</span>
            <br />
            или перетащите сюда файл
          </p>
          {helpText && <p className="text-xs text-foreground text-center">{helpText}</p>}
        </div>
      </FileInput>
      <FileUploaderContent>
        {props.value &&
          props.value.length > 0 &&
          props.value.map((file, idx) => (
            <FileUploaderItem key={idx} index={idx}>
              <Paperclip className="h-4 w-4 stroke-current" />
              <span>{getFilename(file.name)}</span>
            </FileUploaderItem>
          ))}
      </FileUploaderContent>
    </FileUploader>
  )
}

export { FileUploadField }
