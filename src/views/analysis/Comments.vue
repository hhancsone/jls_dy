<template>
  <div class="comments-wrapper">
    <div class="comments-container">
      <h2 class="comments-title">评论详情</h2>
      
      <div class="video-selector">
        <label>选择视频：</label>
        <div class="video-search">
          <input 
            type="text" 
            v-model="searchKeyword" 
            placeholder="搜索视频标题..."
            :disabled="loading"
          />
          <button class="search-btn" @click="handleSearch" :disabled="loading">
            <i class="fa fa-search"></i>
          </button>
          <div v-if="showDropdown && filteredVideos.length > 0" class="video-dropdown">
            <div 
              v-for="video in filteredVideos" 
              :key="video.id" 
              class="video-dropdown-item"
              @click="selectVideo(video)"
            >
              {{ video.title || '未命名视频' }}
            </div>
          </div>
        </div>
        <button class="load-btn" @click="handleLoad" :disabled="loading || !selectedVideoId">
          <i class="fa fa-refresh" :class="{ 'fa-spin': loading }"></i>
          加载评论
        </button>
        <button class="reset-btn" @click="handleReset" :disabled="loading">
          <i class="fa fa-undo"></i>
          重置
        </button>
      </div>

      <div v-if="loading" class="loading">
        <i class="fa fa-spinner fa-spin"></i>
        <span>加载中...</span>
      </div>

      <div v-if="error" class="error">
        <i class="fa fa-exclamation-circle"></i>
        <span>{{ error }}</span>
      </div>

      <div v-if="!loading && !error && !selectedVideoId" class="placeholder">
        <i class="fa fa-comments"></i>
        <p>请选择一个视频查看评论</p>
      </div>

      <div v-if="!loading && !error && selectedVideoId && commentsData && commentsData.length > 0" class="comments-section">
        <div class="comments-header">
          <h3>评论列表</h3>
          <span class="total-count">共 {{ commentsData.length }} 条评论</span>
        </div>

        <div class="comments-list">
          <div v-for="(comment, index) in paginatedComments" :key="index" class="comment-item">
            <div class="comment-header">
              <div class="comment-user">
                <i class="fa fa-user"></i>
                <span class="nickname">{{ comment.user_name || comment.nickname || '匿名用户' }}</span>
                <span v-if="comment.region" class="region">{{ comment.region }}</span>
              </div>
              <div class="comment-date">
                <i class="fa fa-clock"></i>
                <span>{{ formatDate(comment.created_at || comment.date) }}</span>
              </div>
            </div>
            <div class="comment-content">
              {{ comment.content || comment.comment }}
            </div>
          </div>
        </div>

        <div v-if="totalPages > 1" class="pagination">
          <button 
            @click="changePage(currentPage - 1)" 
            :disabled="currentPage === 1"
            class="pagination-button"
          >
            <i class="fa fa-chevron-left"></i>
          </button>
          <template v-for="(page, index) in displayPages" :key="index">
            <span 
              v-if="page === '...'"
              class="pagination-ellipsis"
            >
              ...
            </span>
            <span 
              v-else
              @click="changePage(page)"
              :class="['pagination-number', { active: currentPage === page }]"
            >
              {{ page }}
            </span>
          </template>
          <button 
            @click="changePage(currentPage + 1)" 
            :disabled="currentPage === totalPages"
            class="pagination-button"
          >
            <i class="fa fa-chevron-right"></i>
          </button>
        </div>
      </div>

      <div v-if="!loading && !error && selectedVideoId && commentsData && commentsData.length === 0" class="no-comments">
        <i class="fa fa-inbox"></i>
        <p>暂无评论数据</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const videos = ref([])
const selectedVideoId = ref('')
const selectedVideo = ref(null)
const commentsData = ref([])
const loading = ref(false)
const error = ref('')
const searchKeyword = ref('')
const showDropdown = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)

const filteredVideos = computed(() => {
  if (!searchKeyword.value) return videos.value
  const keyword = searchKeyword.value.toLowerCase()
  return videos.value.filter(v => 
    (v.title || '').toLowerCase().includes(keyword)
  )
})

const totalPages = computed(() => {
  return Math.ceil(commentsData.value.length / pageSize.value)
})

const paginatedComments = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return commentsData.value.slice(start, end)
})

const displayPages = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  const pages = []
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    } else if (current >= total - 3) {
      pages.push(1)
      pages.push('...')
      for (let i = total - 4; i <= total; i++) {
        pages.push(i)
      }
    } else {
      pages.push(1)
      pages.push('...')
      for (let i = current - 1; i <= current + 1; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    }
  }
  
  return pages
})

const handleSearch = () => {
  showDropdown.value = true
}

const selectVideo = (video) => {
  selectedVideo.value = video
  selectedVideoId.value = video.id
  searchKeyword.value = video.title || '未命名视频'
  showDropdown.value = false
}

const closeDropdown = (event) => {
  if (!event.target.closest('.video-search')) {
    showDropdown.value = false
  }
}

const fetchVideos = async () => {
  try {
    const userStr = localStorage.getItem('user')
    const user = userStr ? JSON.parse(userStr) : {}
    
    const headers = {
      'Content-Type': 'application/json'
    }
    
    if (user.id) {
      headers['x-user-id'] = user.id
    }
    
    const response = await fetch('http://localhost:3001/api/videos', {
      headers
    })
    const data = await response.json()
    if (data.success) {
      videos.value = data.videos
    }
  } catch (err) {
    console.error('获取视频列表失败:', err)
  }
}

const handleLoad = async () => {
  if (!selectedVideo.value) {
    commentsData.value = []
    return
  }

  const video = selectedVideo.value
  if (!video) return

  loading.value = true
  error.value = ''
  commentsData.value = []
  currentPage.value = 1

  try {
    const response = await fetch('http://localhost:5000/api/comments', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        videoId: video.video_id,
        title: video.title
      })
    })

    const data = await response.json()

    if (data.success) {
      commentsData.value = data.comments
    } else {
      error.value = data.message || '加载失败'
    }
  } catch (err) {
    console.error('加载评论失败:', err)
    error.value = '加载失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  selectedVideoId.value = ''
  selectedVideo.value = null
  searchKeyword.value = ''
  commentsData.value = []
  error.value = ''
  currentPage.value = 1
  showDropdown.value = false
}

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '未知时间'
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN')
  } catch {
    return dateString
  }
}

onMounted(() => {
  fetchVideos()
  document.addEventListener('click', closeDropdown)
})

onUnmounted(() => {
  document.removeEventListener('click', closeDropdown)
})
</script>

<style scoped>
.comments-wrapper {
  padding: 2rem;
  background-color: #f5f7fa;
  min-height: 100vh;
  margin-left: 16rem;
}

.comments-container {
  width: 100%;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.comments-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.video-selector {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background-color: #f9fafb;
  border-radius: 8px;
}

.video-selector label {
  font-weight: 500;
  color: #374151;
  white-space: nowrap;
}

.video-search {
  position: relative;
  flex: 1;
  display: flex;
  gap: 0.5rem;
}

.video-search input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
  background-color: white;
  cursor: text;
  transition: border-color 0.2s;
}

.video-search input:hover {
  border-color: #3b82f6;
}

.video-search input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.video-search input:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
}

.search-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 1rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.search-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.search-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
  opacity: 0.6;
}

.search-btn i {
  font-size: 1rem;
}

.video-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 300px;
  overflow-y: auto;
  background-color: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 10;
  margin-top: 4px;
}

.video-dropdown-item {
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid #f3f4f6;
}

.video-dropdown-item:last-child {
  border-bottom: none;
}

.video-dropdown-item:hover {
  background-color: #f3f4f6;
}

.load-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1.25rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.load-btn:hover:not(:disabled) {
  background-color: #2563eb;
  transform: translateY(-1px);
}

.load-btn:active:not(:disabled) {
  transform: translateY(0);
}

.load-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
  opacity: 0.6;
}

.load-btn i {
  font-size: 0.9rem;
}

.reset-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1.25rem;
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.reset-btn:hover:not(:disabled) {
  background-color: #dc2626;
  transform: translateY(-1px);
}

.reset-btn:active:not(:disabled) {
  transform: translateY(0);
}

.reset-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
  opacity: 0.6;
}

.reset-btn i {
  font-size: 0.9rem;
}

.loading,
.error,
.placeholder,
.no-comments {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
  color: #6b7280;
}

.loading i,
.error i,
.placeholder i,
.no-comments i {
  font-size: 3rem;
}

.placeholder i {
  color: #3b82f6;
}

.loading span,
.error span,
.placeholder p,
.no-comments p {
  font-size: 1rem;
}

.error {
  color: #ef4444;
}

.placeholder,
.no-comments {
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  background-color: #f9fafb;
}

.comments-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.comments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #f9fafb;
  border-radius: 8px;
}

.comments-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.total-count {
  font-size: 0.9rem;
  color: #6b7280;
  background-color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.comment-item {
  padding: 1.25rem;
  background-color: #f9fafb;
  border-radius: 8px;
  transition: all 0.2s;
}

.comment-item:hover {
  background-color: #f3f4f6;
  transform: translateX(4px);
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  gap: 1rem;
}

.comment-user {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.comment-user i {
  color: #3b82f6;
  font-size: 1rem;
}

.nickname {
  font-weight: 600;
  color: #1f2937;
}

.region {
  font-size: 0.85rem;
  color: #6b7280;
  background-color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.comment-date {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #6b7280;
}

.comment-date i {
  font-size: 0.85rem;
}

.comment-content {
  color: #374151;
  line-height: 1.6;
  word-wrap: break-word;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
}

.pagination-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background-color: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  color: #374151;
}

.pagination-button:hover:not(:disabled) {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.pagination-button:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
  opacity: 0.5;
}

.pagination-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background-color: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  color: #374151;
  font-weight: 500;
}

.pagination-number:hover {
  background-color: #f3f4f6;
}

.pagination-number.active {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.pagination-ellipsis {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  color: #6b7280;
  font-size: 1rem;
}
</style>
