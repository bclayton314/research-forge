import { useState } from 'react'

import {
  type Document,
  chunkDocument,
  embedDocument,
  processDocument,
} from '../api/api'


type DocumentListProps = {
  documents: Document[]
  onRefresh: () => Promise<void>
}


function formatSize(
  bytes: number | null,
): string {
  if (bytes === null) {
    return 'Unknown'
  }

  if (bytes < 1024) {
    return `${bytes} B`
  }

  if (bytes < 1024 * 1024) {
    return `${(
      bytes / 1024
    ).toFixed(1)} KB`
  }

  return `${(
    bytes /
    (1024 * 1024)
  ).toFixed(1)} MB`
}


function DocumentList({
  documents,
  onRefresh,
}: DocumentListProps) {
  const [workingId, setWorkingId] =
    useState<string | null>(null)

  const [error, setError] =
    useState<string | null>(null)


  async function prepareDocument(
    document: Document,
  ) {
    try {
      setWorkingId(document.id)
      setError(null)

      let currentStatus =
        document.status

      if (
        currentStatus === 'uploaded' ||
        currentStatus === 'failed'
      ) {
        const processed =
          await processDocument(
            document.id,
          )

        currentStatus =
          processed.status
      }

      if (
        currentStatus === 'processed'
      ) {
        const chunked =
          await chunkDocument(
            document.id,
          )

        currentStatus =
          chunked.status
      }

      if (
        currentStatus === 'chunked'
      ) {
        const embedded =
          await embedDocument(
            document.id,
          )

        currentStatus =
          embedded.status
      }

      await onRefresh()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Document preparation failed',
      )

      await onRefresh()
    } finally {
      setWorkingId(null)
    }
  }


  return (
    <section className="panel">
      <h2>Documents</h2>

      {error && (
        <p className="error">
          {error}
        </p>
      )}

      {documents.length === 0 ? (
        <p className="muted">
          No documents uploaded yet.
        </p>
      ) : (
        <div className="document-list">
          {documents.map((document) => {
            const isWorking =
              workingId === document.id

            return (
              <article
                className="document-card"
                key={document.id}
              >
                <div>
                  <h3>
                    {document.original_filename}
                  </h3>

                  <p>
                    Status:{' '}
                    <strong>
                      {document.status}
                    </strong>
                  </p>

                  <p className="muted">
                    {document.content_type ??
                      'Unknown type'}
                    {' · '}
                    {formatSize(
                      document.size_bytes,
                    )}
                  </p>
                </div>

                {document.status !==
                  'embedded' && (
                  <button
                    type="button"
                    disabled={isWorking}
                    onClick={() =>
                      prepareDocument(document)
                    }
                  >
                    {isWorking
                      ? 'Preparing...'
                      : 'Prepare'}
                  </button>
                )}

                {document.status ===
                  'embedded' && (
                  <span className="ready-badge">
                    Search ready
                  </span>
                )}
              </article>
            )
          })}
        </div>
      )}
    </section>
  )
}


export default DocumentList