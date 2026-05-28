const API_BASE_URL =
  "http://127.0.0.1:8000"


export async function apiRequest(
  endpoint: string,
  options: RequestInit = {}
) {

  const token =
    localStorage.getItem(
      "access_token"
    )

  const headers = {
    ...(token && {
      Authorization:
        `Bearer ${token}`
    }),

    ...options.headers
  }

  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      ...options,
      headers
    }
  )

  return response.json()
}