import {
  useCallback,
  useEffect,
  useState,
} from 'react'

import {
  type Document,
  type SystemStatusResponse,
  getDocuments,
  getHealth,
  getSystemStatus,
} from './api/api'

import AskPanel from './components/AskPanel'
import DocumentList from './components/DocumentList'
import DocumentUploader from './components/DocumentUploader'
import SearchPanel from './components/SearchPanel'

import './App.css'

function App() {
  const [apiStatus, setApiStatus] =
    useState('Checking...')

  const [systemStatus, setSystemStatus] =
    useState<SystemStatusResponse | null>(
      null,
    )

  const [documents, setDocuments] =
    useState<Document[]>([])

  const [
    loadingDocuments,
    setLoadingDocuments,
  ] = useState(true)

  const [
    documentError,
    setDocumentError,
  ] = useState<string | null>(null)

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

  const loadSystemStatus =
    useCallback(
      async () => {
        try {
          const status =
            await getSystemStatus()

          setSystemStatus(status)
        } catch {
          setSystemStatus(null)
        }
      },
      [],
    )

  useEffect(() => {
    async function initialize() {
      try {
        const health =
          await getHealth()

        setApiStatus(
          health.status,
        )
      } catch {
        setApiStatus(
          'unavailable',
        )
      }

      await Promise.all([
        loadDocuments(),
        loadSystemStatus(),
      ])
    }

    initialize()
  }, [
    loadDocuments,
    loadSystemStatus,
  ])

  function handleUploaded(
    document: Document,
  ) {
    setDocuments(
      (current) => [
        document,
        ...current,
      ],
    )

    void loadSystemStatus()
  }

  async function refreshDocuments() {
    await loadDocuments()
    await loadSystemStatus()
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

          {systemStatus && (
            <div className="system-summary">
              <span>
                Documents:{' '}
                {
                  systemStatus
                    .document_count
                }
              </span>

              <span>
                Search ready:{' '}
                {
                  systemStatus
                    .embedded_document_count
                }
              </span>

              <span>
                LLM:{' '}
                {systemStatus.mock_llm
                  ? 'Mock'
                  : systemStatus
                        .openai_configured
                    ? 'Live'
                    : 'Not configured'}
              </span>
            </div>
          )}
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
          onRefresh={
            refreshDocuments
          }
        />
      )}

      <SearchPanel />

      <AskPanel />
    </main>
  )
}

export default App