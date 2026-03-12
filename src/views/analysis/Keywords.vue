<template>
  <div class="keywords-wrapper">
    <div class="keywords-container">
      <h2 class="keywords-title">评论词云图</h2>
      
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
        <div class="keyword-filter">
          <label>最少出现次数：</label>
          <input 
            type="number" 
            v-model.number="minKeywordCount" 
            min="1" 
            placeholder="输入次数"
          />
        </div>
        <button class="generate-btn" @click="handleGenerate" :disabled="loading || !selectedVideoId">
          <i class="fa fa-refresh" :class="{ 'fa-spin': loading }"></i>
          生成词云
        </button>
        <button class="reset-btn" @click="handleReset" :disabled="loading">
          <i class="fa fa-undo"></i>
          重置
        </button>
      </div>

      <div v-if="loading" class="loading">
        <i class="fa fa-spinner fa-spin"></i>
        <span>分析中...</span>
      </div>

      <div v-if="error" class="error">
        <i class="fa fa-exclamation-circle"></i>
        <span>{{ error }}</span>
      </div>

      <div v-if="!selectedVideoId" class="placeholder">
        <i class="fa fa-cloud"></i>
        <p>请选择一个视频进行分析</p>
      </div>

      <div v-if="wordcloudData" class="wordcloud-section">
        <div class="wordcloud-image">
          <img :src="`data:image/png;base64,${wordcloudData.wordcloud}`" alt="词云图" />
        </div>

        <div class="keywords-list">
          <h3>高频关键词</h3>
          <div class="keywords-grid">
            <div v-for="(keyword, index) in filteredKeywords" :key="index" class="keyword-item">
              <span class="keyword-word">{{ keyword.word }}</span>
              <span class="keyword-count">{{ keyword.count }}次</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const videos = ref([])
const selectedVideoId = ref('')
const selectedVideo = ref(null)
const wordcloudData = ref(null)
const loading = ref(false)
const error = ref('')
const minKeywordCount = ref(3)
const searchKeyword = ref('')
const showDropdown = ref(false)

const filteredVideos = computed(() => {
  if (!searchKeyword.value) return videos.value
  const keyword = searchKeyword.value.toLowerCase()
  return videos.value.filter(v => 
    (v.title || '').toLowerCase().includes(keyword)
  )
})

const filteredKeywords = computed(() => {
  if (!wordcloudData.value || !wordcloudData.value.keywords) return []
  return wordcloudData.value.keywords.filter(k => k.count >= minKeywordCount.value)
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

const handleGenerate = async () => {
  if (!selectedVideo.value) {
    wordcloudData.value = null
    return
  }

  const video = selectedVideo.value
  if (!video) return

  loading.value = true
  error.value = ''
  wordcloudData.value = null

  try {
    const response = await fetch('http://localhost:5000/api/wordcloud', {
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
      wordcloudData.value = data
    } else {
      error.value = data.message || '分析失败'
    }
  } catch (err) {
    console.error('词云分析失败:', err)
    error.value = '分析失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  selectedVideoId.value = ''
  selectedVideo.value = null
  searchKeyword.value = ''
  wordcloudData.value = null
  error.value = ''
  minKeywordCount.value = 3
  showDropdown.value = false
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
.keywords-wrapper {
  padding: 2rem;
  background-color: #f5f7fa;
  min-height: 100vh;
  margin-left: 16rem;
}

.keywords-container {
  width: 100%;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.keywords-title {
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

.keyword-filter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.keyword-filter label {
  font-weight: 500;
  color: #374151;
  white-space: nowrap;
  font-size: 0.9rem;
}

.keyword-filter input {
  width: 80px;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9rem;
  background-color: white;
  transition: border-color 0.2s;
}

.keyword-filter input:hover {
  border-color: #3b82f6;
}

.keyword-filter input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.generate-btn {
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

.generate-btn:hover:not(:disabled) {
  background-color: #2563eb;
  transform: translateY(-1px);
}

.generate-btn:active:not(:disabled) {
  transform: translateY(0);
}

.generate-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
  opacity: 0.6;
}

.generate-btn i {
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
.placeholder {
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
.placeholder i {
  font-size: 3rem;
}

.placeholder i {
  color: #3b82f6;
}

.loading span,
.error span,
.placeholder p {
  font-size: 1rem;
}

.error {
  color: #ef4444;
}

.placeholder {
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  background-color: #f9fafb;
}

.wordcloud-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.wordcloud-image {
  text-align: center;
  padding: 1rem;
  background-color: #f9fafb;
  border-radius: 8px;
}

.wordcloud-image img {
  max-width: 60%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.keywords-list {
  background-color: #f9fafb;
  padding: 1.5rem;
  border-radius: 8px;
}

.keywords-list h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.keywords-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.keyword-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: white;
  border-radius: 6px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
}

.keyword-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.keyword-word {
  font-weight: 500;
  color: #1f2937;
}

.keyword-count {
  font-size: 0.875rem;
  color: #6b7280;
  background-color: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}
</style>