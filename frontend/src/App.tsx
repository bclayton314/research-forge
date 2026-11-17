import {
  useCallback,
  useEffect,
  useState,
} from 'react'

import {
  type Document,
  getDocuments,
  getHealth,
} from './api/api'

import DocumentList from './components/DocumentList'
import DocumentUploader from './components/DocumentUploader'
import SearchPanel from './components/SearchPanel'

import './App.css'


function App() {
  const [apiStatus, setApiStatus] =
    useState('Checking...')

  const [documents, setDocuments] =
    useState<Document[]>([])

  const [loadingDocuments, setLoadingDocuments] =
    useState(true)

  const [documentError, setDocumentError] =
    useState<string | null>(null)


  const loadDocuments = useCallback(
    async () => {
      try {
        setDocumentError(null)

        const response =
          await getDocuments()

        setDocuments(
          response.documents,
        )
      } catch (err) {
        setDocumentError(
          err instanceof Error
            ? err.message
            : 'Unable to load documents',
        )
      } finally {
        setLoadingDocuments(false)
      }
    },
    [],
  )


  useEffect(() => {
    async function initialize() {
      try {
        const health =
          await getHealth()

        setApiStatus(health.status)
      } catch {
        setApiStatus('unavailable')
      }

      await loadDocuments()
    }

    initialize()
  }, [loadDocuments])


  function handleUploaded(
    document: Document,
  ) {
    setDocuments(
      (current) => [
        document,
        ...current,
      ],
    )
  }


  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <h1>ResearchForge</h1>

          <p>
            AI-powered research and
            document analysis.
          </p>
        </div>

        <div className="api-status">
          API:{' '}
          <strong>
            {apiStatus}
          </strong>
        </div>
      </header>

      <DocumentUploader
        onUploaded={handleUploaded}
      />

      {documentError && (
        <p className="error">
          {documentError}
        </p>
      )}

      {loadingDocuments ? (
        <section className="panel">
          <p>
            Loading documents...
          </p>
        </section>
      ) : (
        <DocumentList
          documents={documents}
          onRefresh={loadDocuments}
        />
      )}

      <SearchPanel />
    </main>
  )
}


export default App