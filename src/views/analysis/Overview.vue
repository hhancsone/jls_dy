<template>
  <div class="overview-wrapper">
    <div class="overview-container">
      <h2 class="overview-title">情感分布分析</h2>
      
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
        <label>选择模型：</label>
        <div class="model-selector">
          <select v-model="selectedModel" :disabled="loading">
            <option value="random_forest">随机森林</option>
            <option value="naive_bayes">朴素贝叶斯</option>
            <option value="logistic_regression">逻辑回归</option>
            <option value="svm">支持向量机</option>
            <option value="gradient_boosting">梯度提升</option>
          </select>
        </div>
        <button class="analyze-btn" @click="handleAnalyze" :disabled="loading || !selectedVideoId">
          <i class="fa fa-refresh" :class="{ 'fa-spin': loading }"></i>
          开始分析
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
        <i class="fa fa-pie-chart"></i>
        <p>请选择一个视频进行分析</p>
      </div>

      <div v-if="sentimentData" class="sentiment-section">
        <div class="sentiment-stats">
          <h3>情感分布统计 <small style="font-size: 0.875rem; font-weight: normal; color: #6b7280;">(点击卡片查看评论)</small></h3>
          <div class="stats-grid">
            <div class="stat-card positive" @click="showComments('positive')">
              <div class="stat-info">
                <p class="stat-label">正面评论</p>
                <h3 class="stat-value">{{ sentimentData.stats.positive }}</h3>
                <div class="stat-ratio">{{ sentimentData.stats.positive_ratio }}%</div>
              </div>
              <div class="stat-icon">
                <i class="fa fa-smile-o"></i>
              </div>
            </div>
            <div class="stat-card negative" @click="showComments('negative')">
              <div class="stat-info">
                <p class="stat-label">负面评论</p>
                <h3 class="stat-value">{{ sentimentData.stats.negative }}</h3>
                <div class="stat-ratio">{{ sentimentData.stats.negative_ratio }}%</div>
              </div>
              <div class="stat-icon">
                <i class="fa fa-frown-o"></i>
              </div>
            </div>
            <div class="stat-card neutral" @click="showComments('neutral')">
              <div class="stat-info">
                <p class="stat-label">中性评论</p>
                <h3 class="stat-value">{{ sentimentData.stats.neutral }}</h3>
                <div class="stat-ratio">{{ sentimentData.stats.neutral_ratio }}%</div>
              </div>
              <div class="stat-icon">
                <i class="fa fa-meh-o"></i>
              </div>
            </div>
          </div>
        </div>

        <div v-if="showCommentsList" class="comments-section">
          <div class="comments-header">
            <h3>{{ commentsTitle }}</h3>
            <button class="close-comments-btn" @click="closeComments">
              <i class="fa fa-times"></i>
            </button>
          </div>
          <div v-if="commentsLoading" class="comments-loading">
            <i class="fa fa-spinner fa-spin"></i>
            <span>加载中...</span>
          </div>
          <div v-else-if="comments.length > 0" class="comments-list">
            <div v-for="comment in comments" :key="comment.id" class="comment-item">
              <div class="comment-header">
                <span class="comment-user">{{ comment.user_name || '匿名用户' }}</span>
                <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
              </div>
              <div class="comment-content">{{ comment.content }}</div>
              <div class="comment-sentiment" :class="getSentimentClass(comment.sentiment)">
                {{ getSentimentLabel(comment.sentiment) }}
              </div>
            </div>
          </div>
          <div v-else class="no-comments">
            <i class="fa fa-inbox"></i>
            <p>暂无评论</p>
          </div>
        </div>

        <div class="sentiment-chart">
          <h3>情感分布图</h3>
          <div class="chart-container">
            <canvas ref="chartCanvas"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import Chart from 'chart.js/auto'

const videos = ref([])
const selectedVideoId = ref('')
const selectedVideo = ref(null)
const selectedModel = ref('random_forest')
const sentimentData = ref(null)
const loading = ref(false)
const error = ref('')
const searchKeyword = ref('')
const showDropdown = ref(false)
const chartCanvas = ref(null)
const showCommentsList = ref(false)
const comments = ref([])
const commentsLoading = ref(false)
const commentsTitle = ref('')
let chartInstance = null

const filteredVideos = computed(() => {
  if (!searchKeyword.value) return videos.value
  const keyword = searchKeyword.value.toLowerCase()
  return videos.value.filter(v => 
    (v.title || '').toLowerCase().includes(keyword)
  )
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

const handleAnalyze = async () => {
  if (!selectedVideo.value) {
    sentimentData.value = null
    return
  }

  const video = selectedVideo.value
  if (!video) return

  loading.value = true
  error.value = ''
  sentimentData.value = null

  try {
    const response = await fetch('http://localhost:5000/api/sentiment', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        videoId: video.video_id,
        title: video.title,
        model: selectedModel.value
      })
    })

    const data = await response.json()

    if (data.success) {
      sentimentData.value = data
      await nextTick()
      renderChart()
    } else {
      error.value = data.message || '分析失败'
    }
  } catch (err) {
    console.error('情感分析失败:', err)
    error.value = '分析失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  selectedVideoId.value = ''
  selectedVideo.value = null
  searchKeyword.value = ''
  sentimentData.value = null
  error.value = ''
  showDropdown.value = false
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
}

const renderChart = () => {
  if (!chartCanvas.value || !sentimentData.value) return

  const ctx = chartCanvas.value.getContext('2d')
  const stats = sentimentData.value.stats

  if (chartInstance) {
    chartInstance.destroy()
  }

  chartInstance = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['正面评论', '负面评论', '中性评论'],
      datasets: [{
        data: [stats.positive, stats.negative, stats.neutral],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(156, 163, 175, 0.8)'
        ],
        borderColor: [
          'rgb(34, 197, 94)',
          'rgb(239, 68, 68)',
          'rgb(156, 163, 175)'
        ],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 20,
            font: {
              size: 14
            }
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.label || ''
              const value = context.parsed || 0
              const total = context.dataset.data.reduce((a, b) => a + b, 0)
              const percentage = ((value / total) * 100).toFixed(2)
              return `${label}: ${value} (${percentage}%)`
            }
          }
        }
      }
    }
  })
}

const showComments = async (sentiment) => {
  console.log('=== 点击事件触发 ===')
  console.log('情感类型:', sentiment)
  console.log('选中的视频:', selectedVideo.value)
  console.log('视频ID:', selectedVideo.value?.id)
  console.log('视频标题:', selectedVideo.value?.title)
  console.log('使用的模型:', selectedModel.value)
  
  if (!selectedVideo.value) {
    console.log('❌ 没有选中视频，无法显示评论')
    alert('请先选择一个视频')
    return
  }
  
  const titleMap = {
    'positive': '正面评论',
    'negative': '负面评论',
    'neutral': '中性评论'
  }
  
  commentsTitle.value = titleMap[sentiment]
  showCommentsList.value = true
  commentsLoading.value = true
  comments.value = []
  
  console.log('✓ 开始获取评论')
  console.log('video_id:', selectedVideo.value.id, 'title:', selectedVideo.value.title, 'sentiment:', sentiment, 'model:', selectedModel.value)
  
  try {
    const userStr = localStorage.getItem('user')
    const user = userStr ? JSON.parse(userStr) : {}
    
    const headers = {
      'Content-Type': 'application/json'
    }
    
    if (user.id) {
      headers['x-user-id'] = user.id
    }
    
    const url = `http://localhost:3001/api/comments?video_id=${selectedVideo.value.id}&title=${encodeURIComponent(selectedVideo.value.title)}&sentiment=${sentiment}&model=${selectedModel.value}`
    
    console.log('请求URL:', url)
    const response = await fetch(url, { headers })
    const data = await response.json()
    
    console.log('评论数据响应:', data)
    
    if (data.success) {
      comments.value = data.comments || []
      console.log('✓ 成功获取评论，数量:', comments.value.length)
    } else {
      comments.value = []
      console.log('❌ 获取评论失败:', data.message)
    }
  } catch (err) {
    console.error('❌ 获取评论失败:', err)
    comments.value = []
  } finally {
    commentsLoading.value = false
  }
}

const closeComments = () => {
  showCommentsList.value = false
  comments.value = []
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const getSentimentLabel = (sentiment) => {
  const labels = {
    'positive': '正面',
    'negative': '负面',
    'neutral': '中性'
  }
  return labels[sentiment] || '未知'
}

const getSentimentClass = (sentiment) => {
  return `sentiment-${sentiment}`
}

onMounted(() => {
  fetchVideos()
  document.addEventListener('click', closeDropdown)
})

onUnmounted(() => {
  document.removeEventListener('click', closeDropdown)
  if (chartInstance) {
    chartInstance.destroy()
  }
})
</script>

<style scoped>
.overview-wrapper {
  padding: 2rem;
  background-color: #f5f7fa;
  min-height: 100vh;
  margin-left: 16rem;
}

.overview-container {
  width: 100%;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.overview-title {
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

.model-selector {
  display: flex;
  align-items: center;
}

.model-selector select {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
  background-color: white;
  cursor: pointer;
  transition: border-color 0.2s;
  min-width: 150px;
}

.model-selector select:hover {
  border-color: #9ca3af;
}

.model-selector select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.model-selector select:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
  opacity: 0.6;
}

.analyze-btn {
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

.analyze-btn:hover:not(:disabled) {
  background-color: #2563eb;
  transform: translateY(-1px);
}

.analyze-btn:active:not(:disabled) {
  transform: translateY(0);
}

.analyze-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
  opacity: 0.6;
}

.analyze-btn i {
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

.sentiment-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.sentiment-stats h3,
.sentiment-chart h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
  background-color: #ffffff;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-card.positive .stat-icon {
  background-color: #dcfce7;
}

.stat-card.positive .stat-icon i {
  color: #16a34a;
}

.stat-card.negative .stat-icon {
  background-color: #fee2e2;
}

.stat-card.negative .stat-icon i {
  color: #dc2626;
}

.stat-card.neutral .stat-icon {
  background-color: #f3f4f6;
}

.stat-card.neutral .stat-icon i {
  color: #6b7280;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon i {
  font-size: 1.25rem;
  color: #6b7280;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.stat-ratio {
  font-size: 0.875rem;
  color: #9ca3af;
}

.sentiment-chart {
  background-color: #ffffff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chart-container {
  max-width: 600px;
  margin: 0 auto;
}

.comments-section {
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.comments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.comments-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.close-comments-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  color: #6b7280;
  padding: 0.5rem;
  transition: color 0.2s;
}

.close-comments-btn:hover {
  color: #374151;
}

.comments-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 3rem;
  color: #6b7280;
}

.comments-list {
  max-height: 500px;
  overflow-y: auto;
}

.comment-item {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  transition: background-color 0.2s;
}

.comment-item:hover {
  background-color: #f9fafb;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.comment-user {
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.comment-date {
  color: #9ca3af;
  font-size: 0.875rem;
}

.comment-content {
  color: #4b5563;
  font-size: 0.95rem;
  line-height: 1.6;
  margin-bottom: 0.75rem;
}

.comment-sentiment {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.sentiment-positive {
  background-color: #dcfce7;
  color: #166534;
}

.sentiment-negative {
  background-color: #fee2e2;
  color: #991b1b;
}

.sentiment-neutral {
  background-color: #f3f4f6;
  color: #374151;
}

.no-comments {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #9ca3af;
}

.no-comments i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.no-comments p {
  font-size: 1rem;
  margin: 0;
}
</style>
