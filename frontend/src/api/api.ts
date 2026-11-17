export type HealthResponse = {
  service: string
  status: string
}

export type Document = {
  id: string
  filename: string
  original_filename: string
  content_type: string | null
  size_bytes: number | null
  storage_key: string | null
  status: string
  extracted_text: string | null
  created_at: string | null
  updated_at: string | null
}

export type DocumentListResponse = {
  documents: Document[]
}

export type ProcessDocumentResponse = Document

export type ChunkDocumentResponse = {
  document_id: string
  status: string
  chunk_count: number
}

export type EmbedDocumentResponse = {
  document_id: string
  status: string
  embedded_chunk_count: number
}

export type KeywordSearchResult = {
  document_id: string
  document_name: string
  chunk_id: string
  chunk_index: number
  score: number
  snippet: string
}

export type KeywordSearchResponse = {
  query: string
  result_count: number
  results: KeywordSearchResult[]
}

export type SemanticSearchResult = {
  document_id: string
  document_name: string
  chunk_id: string
  chunk_index: number
  similarity: number
  text: string
}

export type SemanticSearchResponse = {
  query: string
  result_count: number
  results: SemanticSearchResult[]
}

export type HybridSearchResult = {
  document_id: string
  document_name: string
  chunk_id: string
  chunk_index: number
  keyword_score: number | null
  semantic_score: number | null
  rrf_score: number
  matched_keyword: boolean
  matched_semantic: boolean
  text: string
}

export type HybridSearchResponse = {
  query: string
  strategy: string
  result_count: number
  results: HybridSearchResult[]
}


async function request<T>(
  url: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(url, options)

  if (!response.ok) {
    const data = await response
      .json()
      .catch(() => null)

    const message =
      data?.error ??
      `Request failed with status ${response.status}`

    throw new Error(message)
  }

  return response.json()
}


export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>(
    '/api/health',
  )
}


export function getDocuments(): Promise<DocumentListResponse> {
  return request<DocumentListResponse>(
    '/api/documents',
  )
}


export async function uploadDocument(
  file: File,
): Promise<Document> {
  const formData = new FormData()

  formData.append(
    'file',
    file,
  )

  return request<Document>(
    '/api/documents/upload',
    {
      method: 'POST',
      body: formData,
    },
  )
}


export function processDocument(
  documentId: string,
): Promise<ProcessDocumentResponse> {
  return request<ProcessDocumentResponse>(
    `/api/documents/${documentId}/process`,
    {
      method: 'POST',
    },
  )
}


export function chunkDocument(
  documentId: string,
): Promise<ChunkDocumentResponse> {
  return request<ChunkDocumentResponse>(
    `/api/documents/${documentId}/chunk`,
    {
      method: 'POST',
    },
  )
}


export function embedDocument(
  documentId: string,
): Promise<EmbedDocumentResponse> {
  return request<EmbedDocumentResponse>(
    `/api/documents/${documentId}/embed`,
    {
      method: 'POST',
    },
  )
}


export function keywordSearch(
  query: string,
): Promise<KeywordSearchResponse> {
  const params = new URLSearchParams({
    q: query,
  })

  return request<KeywordSearchResponse>(
    `/api/search?${params.toString()}`,
  )
}


export function semanticSearch(
  query: string,
): Promise<SemanticSearchResponse> {
  const params = new URLSearchParams({
    q: query,
  })

  return request<SemanticSearchResponse>(
    `/api/search/semantic?${params.toString()}`,
  )
}


export function hybridSearch(
  query: string,
): Promise<HybridSearchResponse> {
  const params = new URLSearchParams({
    q: query,
  })

  return request<HybridSearchResponse>(
    `/api/search/hybrid?${params.toString()}`,
  )
}
