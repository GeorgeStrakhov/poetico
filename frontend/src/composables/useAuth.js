export function useAuth() {
  const getAuthHeaders = () => {
    const token = localStorage.getItem('auth_token')
    return token ? {
      'Authorization': `Bearer ${token}`
    } : {}
  }

  const isAuthenticated = () => {
    return !!localStorage.getItem('auth_token')
  }

  return {
    getAuthHeaders,
    isAuthenticated
  }
} 