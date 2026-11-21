import {
  type FormEvent,
  useState,
} from 'react'

import {
  type AskSource,
  askResearchForge,
} from '../api/api'


function AskPanel() {
  const [question, setQuestion] =
    useState('')

  const [answer, setAnswer] =
    useState<string | null>(null)

  const [sources, setSources] =
    useState<AskSource[]>([])

  const [asking, setAsking] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)


  async function handleSubmit(
    event: FormEvent,
  ) {
    event.preventDefault()

    const trimmedQuestion =
      question.trim()

    if (!trimmedQuestion) {
      return
    }

    try {
      setAsking(true)
      setError(null)
      setAnswer(null)
      setSources([])

      const response =
        await askResearchForge(
          trimmedQuestion,
        )

      setAnswer(response.answer)
      setSources(response.sources)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to answer question',
      )
    } finally {
      setAsking(false)
    }
  }


  return (
    <section className="panel">
      <h2>Ask ResearchForge</h2>

      <p className="muted">
        Ask a question grounded in your
        uploaded research documents.
      </p>

      <form
        className="ask-form"
        onSubmit={handleSubmit}
      >
        <textarea
          value={question}
          placeholder="What do the documents say about...?"
          rows={4}
          onChange={(event) =>
            setQuestion(
              event.target.value,
            )
          }
        />

        <button
          type="submit"
          disabled={
            asking ||
            !question.trim()
          }
        >
          {asking
            ? 'Researching...'
            : 'Ask'}
        </button>
      </form>

      {error && (
        <p className="error">
          {error}
        </p>
      )}

      {answer && (
        <div className="answer-panel">
          <h3>Answer</h3>

          <p className="answer-text">
            {answer}
          </p>
        </div>
      )}

      {sources.length > 0 && (
        <div className="sources-panel">
          <h3>Sources</h3>

          <div className="source-list">
            {sources.map((source) => (
              <article
                className="source-card"
                key={source.chunk_id}
              >
                <div className="source-main">
                  <strong>
                    [{source.label}]
                  </strong>

                  <span>
                    {source.document_name}
                  </span>
                </div>

                <div className="source-meta">
                  <span>
                    Chunk {source.chunk_index + 1}
                  </span>

                  <span>
                    Retrieval score:{' '}
                    {source.rrf_score.toFixed(4)}
                  </span>
                </div>
              </article>
            ))}
          </div>
        </div>
      )}
    </section>
  )
}


export default AskPanel