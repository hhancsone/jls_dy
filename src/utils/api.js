const API_BASE_URL = '/api'
const PYTHON_API_BASE_URL = 'http://localhost:5000'

export const api = {
  async request(url, options = {}) {
    try {
      const userStr = localStorage.getItem('user')
      const user = userStr ? JSON.parse(userStr) : {}
      
      const headers = {
        'Content-Type': 'application/json',
        ...options.headers
      }

      if (user.id) {
        headers['x-user-id'] = user.id
      }

      const response = await fetch(url, {
        headers,
        ...options
      })

      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.message || '请求失败')
      }
      
      return data
    } catch (error) {
      console.error('API请求错误:', error)
      throw error
    }
  },

  async get(url, options = {}) {
    return this.request(url, { ...options, method: 'GET' })
  },

  async post(url, data, options = {}) {
    return this.request(url, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data)
    })
  },

  async put(url, data, options = {}) {
    return this.request(url, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data)
    })
  },

  async delete(url, options = {}) {
    return this.request(url, { ...options, method: 'DELETE' })
  }
}

export const videoApi = {
  getVideos(searchQuery) {
    let url = `${API_BASE_URL}/videos`
    if (searchQuery) {
      url += `?search=${encodeURIComponent(searchQuery)}`
    }
    return api.get(url)
  },

  getVideoById(id) {
    return api.get(`${API_BASE_URL}/videos/${id}`)
  },

  createVideo(data) {
    return api.post(`${API_BASE_URL}/videos`, data)
  },

  deleteVideo(id) {
    return api.delete(`${API_BASE_URL}/videos/${id}`)
  },

  downloadCsv(id) {
    return `${API_BASE_URL}/videos/${id}/download-csv`
  },

  crawlComments(videoUrl) {
    return api.post(`${API_BASE_URL}/crawl-comments`, { videoUrl })
  }
}

export const userApi = {
  getUsers(searchQuery) {
    let url = `${API_BASE_URL}/users`
    if (searchQuery) {
      url += `?search=${encodeURIComponent(searchQuery)}`
    }
    return api.get(url)
  },

  createUser(data) {
    return api.post(`${API_BASE_URL}/users`, data)
  },

  updateUser(id, data) {
    return api.put(`${API_BASE_URL}/users/${id}`, data)
  },

  deleteUser(id) {
    return api.delete(`${API_BASE_URL}/users/${id}`)
  },

  batchCreateUsers(users) {
    return api.post(`${API_BASE_URL}/users/batch`, { users })
  }
}

export const analysisApi = {
  getComments(data) {
    return api.post(`${PYTHON_API_BASE_URL}/api/comments`, data)
  },

  getSentiment(data) {
    return api.post(`${PYTHON_API_BASE_URL}/api/sentiment`, data)
  },

  getTrend(data) {
    return api.post(`${PYTHON_API_BASE_URL}/api/trend`, data)
  },

  getWordCloud(data) {
    return api.post(`${PYTHON_API_BASE_URL}/api/wordcloud`, data)
  },

  getRegion(data) {
    return api.post(`${PYTHON_API_BASE_URL}/api/region`, data)
  },

  generateReport(data) {
    return api.post(`${PYTHON_API_BASE_URL}/api/generate-report`, data)
  }
}

export const authApi = {
  login(data) {
    return api.post(`${API_BASE_URL}/login`, data)
  },

  register(data) {
    return api.post(`${API_BASE_URL}/register`, data)
  },

  logout() {
    return api.post(`${API_BASE_URL}/logout`)
  },

  getCurrentUser() {
    return api.get(`${API_BASE_URL}/me`)
  },

  changePassword(data) {
    return api.post(`${API_BASE_URL}/change-password`, data)
  }
}
