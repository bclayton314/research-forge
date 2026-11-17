import {
  type FormEvent,
  useState,
} from 'react'

import {
  keywordSearch,
  semanticSearch,
} from '../api/api'


type SearchMode =
  | 'keyword'
  | 'semantic'


type SearchResult = {
  documentId: string
  documentName: string
  chunkIndex: number
  score: number
  text: string
}


function SearchPanel() {
  const [query, setQuery] = useState('')
  const [mode, setMode] =
    useState<SearchMode>('semantic')

  const [results, setResults] =
    useState<SearchResult[]>([])

  const [searching, setSearching] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)


  async function handleSearch(
    event: FormEvent,
  ) {
    event.preventDefault()

    const trimmedQuery = query.trim()

    if (!trimmedQuery) {
      return
    }

    try {
      setSearching(true)
      setError(null)

      if (mode === 'keyword') {
        const response =
          await keywordSearch(trimmedQuery)

        setResults(
          response.results.map(
            (result) => ({
              documentId:
                result.document_id,
              documentName:
                result.document_name,
              chunkIndex:
                result.chunk_index,
              score: result.score,
              text: result.snippet,
            }),
          ),
        )
      } else {
        const response =
          await semanticSearch(
            trimmedQuery,
          )

        setResults(
          response.results.map(
            (result) => ({
              documentId:
                result.document_id,
              documentName:
                result.document_name,
              chunkIndex:
                result.chunk_index,
              score:
                result.similarity,
              text: result.text,
            }),
          ),
        )
      }
    } catch (err) {
      setResults([])

      setError(
        err instanceof Error
          ? err.message
          : 'Search failed',
      )
    } finally {
      setSearching(false)
    }
  }


  return (
    <section className="panel">
      <h2>Search Research</h2>

      <form
        className="search-form"
        onSubmit={handleSearch}
      >
        <input
          type="search"
          value={query}
          placeholder="Search your research..."
          onChange={(event) =>
            setQuery(event.target.value)
          }
        />

        <select
          value={mode}
          onChange={(event) =>
            setMode(
              event.target.value as SearchMode,
            )
          }
        >
          <option value="semantic">
            Semantic
          </option>

          <option value="keyword">
            Keyword
          </option>
        </select>

        <button
          type="submit"
          disabled={
            searching ||
            !query.trim()
          }
        >
          {searching
            ? 'Searching...'
            : 'Search'}
        </button>
      </form>

      {error && (
        <p className="error">
          {error}
        </p>
      )}

      <div className="search-results">
        {results.map(
          (result, index) => (
            <article
              className="search-result"
              key={`${result.documentId}-${result.chunkIndex}-${index}`}
            >
              <div className="result-heading">
                <strong>
                  {result.documentName}
                </strong>

                <span>
                  Chunk {result.chunkIndex + 1}
                </span>
              </div>

              <p>{result.text}</p>

              <small>
                {mode === 'semantic'
                  ? `Similarity: ${result.score.toFixed(3)}`
                  : `Keyword score: ${result.score}`}
              </small>
            </article>
          ),
        )}
      </div>

      {!searching &&
        query &&
        results.length === 0 &&
        !error && (
          <p className="muted">
            No matching passages found.
          </p>
        )}
    </section>
  )
}


export default SearchPanel