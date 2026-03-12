<template>
  <div class="region-distribution-wrapper">
    <div class="region-distribution-container">
      <h2 class="region-distribution-title">地区分布分析</h2>
      
      <div class="video-selector">
        <label>选择视频：</label>
        <div class="video-search">
          <input 
            type="text" 
            v-model="searchKeyword" 
            placeholder="搜索视频标题..."
            :disabled="loading"
            @focus="showDropdown = true"
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
        <div class="region-filter">
          <label>最少评论数：</label>
          <input 
            type="number" 
            v-model.number="minRegionCount" 
            min="1" 
            placeholder="输入次数"
          />
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
        <i class="fa fa-map-marker"></i>
        <p>请选择一个视频进行分析</p>
      </div>

      <div v-if="regionData" class="region-section">
        <div class="region-stats">
          <h3>地区分布统计</h3>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-info">
                <p class="stat-label">总评论数</p>
                <h3 class="stat-value">{{ regionData.total_comments }}</h3>
              </div>
              <div class="stat-icon">
                <i class="fa fa-comments"></i>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-info">
                <p class="stat-label">覆盖地区数</p>
                <h3 class="stat-value">{{ regionData.total_regions }}</h3>
              </div>
              <div class="stat-icon">
                <i class="fa fa-map-marker"></i>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-info">
                <p class="stat-label">最活跃地区</p>
                <h3 class="stat-value">{{ regionData.top_region }}</h3>
              </div>
              <div class="stat-icon">
                <i class="fa fa-star"></i>
              </div>
            </div>
          </div>
        </div>

        <div class="region-chart">
          <h3>地区分布图</h3>
          <div class="chart-container">
            <canvas ref="chartCanvas"></canvas>
          </div>
        </div>

        <div class="region-table">
          <h3>详细数据</h3>
          <table>
            <thead>
              <tr>
                <th>排名</th>
                <th>地区</th>
                <th>评论数</th>
                <th>占比</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in regionData.regions" :key="index">
                <td>{{ index + 1 }}</td>
                <td>{{ item.region }}</td>
                <td>{{ item.count }}</td>
                <td>{{ item.ratio }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import Chart from 'chart.js/auto'

const searchKeyword = ref('')
const selectedVideoId = ref(null)
const selectedVideo = ref(null)
const videos = ref([])
const filteredVideos = ref([])
const showDropdown = ref(false)
const loading = ref(false)
const error = ref('')
const regionData = ref(null)
const chartCanvas = ref(null)
const minRegionCount = ref(3)
let chartInstance = null

const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    filteredVideos.value = []
    showDropdown.value = false
    return
  }
  
  if (videos.value.length === 0) {
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
      return
    }
  }
  
  filteredVideos.value = videos.value.filter(video => 
    (video.title || '').toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
  showDropdown.value = true
}

const selectVideo = (video) => {
  selectedVideoId.value = video.video_id
  selectedVideo.value = video
  searchKeyword.value = video.title || ''
  showDropdown.value = false
}

const handleAnalyze = async () => {
  if (!selectedVideoId.value) {
    regionData.value = null
    return
  }

  const video = selectedVideo.value
  if (!video) return

  loading.value = true
  error.value = ''
  regionData.value = null

  try {
    const response = await fetch('http://localhost:5000/api/region', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        videoId: video.video_id,
        title: video.title,
        minCount: minRegionCount.value
      })
    })

    const data = await response.json()

    if (data.success) {
      regionData.value = data
      await nextTick()
      renderChart()
    } else {
      error.value = data.message || '分析失败'
    }
  } catch (err) {
    console.error('地区分析失败:', err)
    error.value = '分析失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  selectedVideoId.value = null
  selectedVideo.value = null
  searchKeyword.value = ''
  filteredVideos.value = []
  showDropdown.value = false
  regionData.value = null
  error.value = ''
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
}

const renderChart = () => {
  if (!chartCanvas.value || !regionData.value) return

  const ctx = chartCanvas.value.getContext('2d')
  
  if (chartInstance) {
    chartInstance.destroy()
  }

  const labels = regionData.value.regions.slice(0, 10).map(r => r.region)
  const data = regionData.value.regions.slice(0, 10).map(r => r.count)

  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: '评论数',
        data: data,
        backgroundColor: 'rgba(99, 102, 241, 0.8)',
        borderColor: 'rgba(99, 102, 241, 1)',
        borderWidth: 1
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
          callbacks: {
            label: function(context) {
              return `评论数: ${context.raw}`
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          }
        },
        x: {
          ticks: {
            maxRotation: 45,
            minRotation: 45
          }
        }
      }
    }
  })
}

onMounted(() => {
  handleSearch()
})
</script>

<style scoped>
.region-distribution-wrapper {
  padding: 2rem;
  background-color: #f5f7fa;
  min-height: 100vh;
  margin-left: 16rem;
}

.region-distribution-container {
  width: 100%;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.region-distribution-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 2rem;
  text-align: left;
}

.video-selector {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.video-selector label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  white-space: nowrap;
}

.video-search {
  position: relative;
  flex: 1;
  min-width: 300px;
}

.video-search input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.video-search input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.video-search input:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
}

.search-btn {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
  transition: color 0.2s;
}

.search-btn:hover:not(:disabled) {
  color: #6366f1;
}

.search-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.region-filter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.region-filter label {
  font-weight: 500;
  color: #374151;
  white-space: nowrap;
  font-size: 0.9rem;
}

.region-filter input {
  width: 80px;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9rem;
  background-color: white;
  transition: border-color 0.2s;
}

.region-filter input:hover {
  border-color: #6366f1;
}

.region-filter input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.video-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-height: 300px;
  overflow-y: auto;
  z-index: 100;
  margin-top: 0.25rem;
}

.video-dropdown-item {
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 0.875rem;
  color: #374151;
}

.video-dropdown-item:hover {
  background-color: #f3f4f6;
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

.region-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.region-stats h3,
.region-chart h3,
.region-table h3 {
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

.region-chart {
  background-color: #ffffff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chart-container {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
  height: 400px;
}

.region-table {
  background-color: #ffffff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.region-table table {
  width: 100%;
  border-collapse: collapse;
}

.region-table th,
.region-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.region-table th {
  font-weight: 600;
  color: #374151;
  background-color: #f9fafb;
}

.region-table td {
  color: #6b7280;
}

.region-table tr:hover {
  background-color: #f9fafb;
}
</style>
