<template>
  <div class="sentiment-wrapper">
    <div class="sentiment-container">
      <h2 class="sentiment-title">数量趋势</h2>
      
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
        <div class="time-filter">
          <label>时间维度：</label>
          <select v-model="timeDimension" :disabled="loading">
            <option value="daily">按天</option>
            <option value="monthly">按月</option>
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
        <i class="fa fa-line-chart"></i>
        <p>请选择一个视频进行分析</p>
      </div>

      <div v-if="trendData" class="trend-section">
        <div class="trend-stats">
          <h3>统计信息</h3>
          <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-info">
              <p class="stat-label">总评论数</p>
              <h3 class="stat-value">{{ trendData.total_comments }}</h3>
            </div>
            <div class="stat-icon">
              <i class="fa fa-comments"></i>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-info">
              <p class="stat-label">统计天数</p>
              <h3 class="stat-value">{{ trendData.total_days }}</h3>
            </div>
            <div class="stat-icon">
              <i class="fa fa-calendar"></i>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-info">
              <p class="stat-label">统计月数</p>
              <h3 class="stat-value">{{ trendData.total_months }}</h3>
            </div>
            <div class="stat-icon">
              <i class="fa fa-calendar-o"></i>
            </div>
          </div>
        </div>
        </div>

        <div class="trend-chart">
          <h3>数量趋势图</h3>
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
const timeDimension = ref('daily')
const trendData = ref(null)
const loading = ref(false)
const error = ref('')
const searchKeyword = ref('')
const showDropdown = ref(false)
const chartCanvas = ref(null)
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
    trendData.value = null
    return
  }

  const video = selectedVideo.value
  if (!video) return

  loading.value = true
  error.value = ''
  trendData.value = null

  try {
    const response = await fetch('http://localhost:5000/api/trend', {
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
      trendData.value = data
      await nextTick()
      renderChart()
    } else {
      error.value = data.message || '分析失败'
    }
  } catch (err) {
    console.error('趋势分析失败:', err)
    error.value = '分析失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  selectedVideoId.value = ''
  selectedVideo.value = null
  searchKeyword.value = ''
  trendData.value = null
  error.value = ''
  timeDimension.value = 'daily'
  showDropdown.value = false
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
}

const renderChart = () => {
  if (!chartCanvas.value || !trendData.value) return

  const ctx = chartCanvas.value.getContext('2d')
  const data = timeDimension.value === 'daily' ? trendData.value.daily : trendData.value.monthly

  if (chartInstance) {
    chartInstance.destroy()
  }

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map(item => item.date),
      datasets: [{
        label: '评论数量',
        data: data.map(item => item.count),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: 'rgb(59, 130, 246)'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          callbacks: {
            title: function(context) {
              return `日期: ${context[0].label}`
            },
            label: function(context) {
              return `评论数: ${context.parsed.y}`
            }
          }
        }
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: '日期'
          },
          ticks: {
            maxTicksLimit: 10
          }
        },
        y: {
          display: true,
          title: {
            display: true,
            text: '评论数量'
          },
          beginAtZero: true
        }
      }
    }
  })
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
.sentiment-wrapper {
  padding: 2rem;
  background-color: #f5f7fa;
  min-height: 100vh;
  margin-left: 16rem;
}

.sentiment-container {
  width: 100%;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.sentiment-title {
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

.time-filter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.time-filter label {
  font-weight: 500;
  color: #374151;
  white-space: nowrap;
}

.time-filter select {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
  background-color: white;
  cursor: pointer;
  transition: border-color 0.2s;
  min-width: 120px;
}

.time-filter select:hover {
  border-color: #9ca3af;
}

.time-filter select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.time-filter select:disabled {
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

.trend-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.trend-stats h3,
.trend-chart h3 {
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
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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
  margin: 0;
}

.trend-chart {
  background-color: #ffffff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chart-container {
  max-width: 800px;
  margin: 0 auto;
}
</style>
