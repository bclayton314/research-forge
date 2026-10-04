export type HealthResponse = {
  service: string
  status: string
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch('/api/health')

  if (!response.ok) {
    throw new Error('Failed to connect to the API')
  }

  return response.json()
}