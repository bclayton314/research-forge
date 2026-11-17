import {
  type ChangeEvent,
  type FormEvent,
  useState,
} from 'react'

import {
  type Document,
  uploadDocument,
} from '../api/api'


type DocumentUploaderProps = {
  onUploaded: (document: Document) => void
}


function DocumentUploader({
  onUploaded,
}: DocumentUploaderProps) {
  const [file, setFile] = useState<File | null>(
    null,
  )

  const [uploading, setUploading] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)


  function handleFileChange(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    const selectedFile =
      event.target.files?.[0] ?? null

    setFile(selectedFile)
    setError(null)
  }


  async function handleSubmit(
    event: FormEvent,
  ) {
    event.preventDefault()

    if (!file) {
      setError('Choose a PDF or TXT file.')
      return
    }

    try {
      setUploading(true)
      setError(null)

      const document =
        await uploadDocument(file)

      onUploaded(document)
      setFile(null)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Upload failed',
      )
    } finally {
      setUploading(false)
    }
  }


  return (
    <section className="panel">
      <h2>Upload Document</h2>

      <p>
        Add a PDF or TXT research document.
      </p>

      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept=".pdf,.txt"
          onChange={handleFileChange}
          disabled={uploading}
        />

        <button
          type="submit"
          disabled={uploading || !file}
        >
          {uploading
            ? 'Uploading...'
            : 'Upload'}
        </button>
      </form>

      {file && (
        <p className="muted">
          Selected: {file.name}
        </p>
      )}

      {error && (
        <p className="error">
          {error}
        </p>
      )}
    </section>
  )
}


export default DocumentUploader