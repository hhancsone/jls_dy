<template>
  <div class="export-report-wrapper">
    <div class="export-report-container">
      <h2 class="export-report-title">导出分析报告</h2>
      
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
        <button class="reset-btn" @click="handleReset" :disabled="loading">
          <i class="fa fa-undo"></i>
          重置
        </button>
      </div>

      <div v-if="!selectedVideoId" class="placeholder">
        <i class="fa fa-file-text"></i>
        <p>请选择一个视频</p>
      </div>

      <div v-if="selectedVideoId" class="report-content">
        <div class="content-selection">
          <h3>选择报告内容</h3>
          
          <div class="checkbox-group">
            <label class="checkbox-item">
              <input type="checkbox" v-model="reportConfig.quantityTrend" />
              <span>数量趋势</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" v-model="reportConfig.sentimentAnalysis" />
              <span>情感分析</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" v-model="reportConfig.sentimentTrend" />
              <span>情感趋势分析</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" v-model="reportConfig.wordCloud" />
              <span>评论词云图</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" v-model="reportConfig.regionDistribution" />
              <span>分布地区</span>
            </label>
          </div>
        </div>

        <div class="filter-section">
          <h3>筛选条件</h3>
          
          <div v-if="reportConfig.quantityTrend" class="filter-subsection">
            <h4>数量趋势分析</h4>
            <div class="filter-group">
              <label>时间维度：</label>
              <select v-model="reportConfig.trendTimeDimension">
                <option value="daily">按天</option>
                <option value="monthly">按月</option>
              </select>
            </div>
          </div>

          <div v-if="reportConfig.sentimentAnalysis" class="filter-subsection">
            <h4>情感分布分析</h4>
            <div class="filter-group">
              <label>分析模型：</label>
              <select v-model="reportConfig.sentimentModel">
                <option value="random_forest">随机森林</option>
                <option value="naive_bayes">朴素贝叶斯</option>
                <option value="logistic_regression">逻辑回归</option>
                <option value="svm">支持向量机</option>
                <option value="gradient_boosting">梯度提升</option>
              </select>
            </div>
          </div>

          <div v-if="reportConfig.sentimentTrend" class="filter-subsection">
            <h4>情感趋势分析</h4>
            <div class="filter-group">
              <label>时间维度：</label>
              <select v-model="reportConfig.sentimentTrendTimeDimension">
                <option value="daily">按天</option>
                <option value="monthly">按月</option>
              </select>
            </div>
            <div class="filter-group">
              <label>分析模型：</label>
              <select v-model="reportConfig.sentimentTrendModel">
                <option value="random_forest">随机森林</option>
                <option value="naive_bayes">朴素贝叶斯</option>
                <option value="logistic_regression">逻辑回归</option>
                <option value="svm">支持向量机</option>
                <option value="gradient_boosting">梯度提升</option>
              </select>
            </div>
          </div>

          <div v-if="reportConfig.wordCloud" class="filter-subsection">
            <h4>评论词云图</h4>
            <div class="filter-group">
              <label>最少出现次数：</label>
              <input 
                type="number" 
                v-model.number="reportConfig.minKeywordCount" 
                min="1" 
                placeholder="输入次数"
              />
            </div>
          </div>

          <div v-if="reportConfig.regionDistribution" class="filter-subsection">
            <h4>分布地区</h4>
            <div class="filter-group">
              <label>最少评论数：</label>
              <input 
                type="number" 
                v-model.number="reportConfig.minRegionCount" 
                min="1" 
                placeholder="输入次数"
              />
            </div>
          </div>
        </div>

        <button class="generate-btn" @click="handleGenerateReport" :disabled="loading || !hasSelectedContent">
          <i class="fa fa-file-text" :class="{ 'fa-spin': loading }"></i>
          生成报告
        </button>

        <div v-if="loading" class="loading">
          <i class="fa fa-spinner fa-spin"></i>
          <span>生成中...</span>
        </div>

        <div v-if="error" class="error">
          <i class="fa fa-exclamation-circle"></i>
          <span>{{ error }}</span>
        </div>

        <div v-if="reportData" class="report-result">
          <h3>报告预览</h3>
          <div class="report-content-text" v-html="reportData"></div>
          <button class="download-btn" @click="handleDownload">
            <i class="fa fa-download"></i>
            下载报告
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const searchKeyword = ref('')
const selectedVideoId = ref(null)
const selectedVideo = ref(null)
const videos = ref([])
const filteredVideos = ref([])
const showDropdown = ref(false)
const loading = ref(false)
const error = ref('')
const reportData = ref(null)

const reportConfig = ref({
  quantityTrend: false,
  sentimentAnalysis: false,
  sentimentTrend: false,
  wordCloud: false,
  regionDistribution: false,
  trendTimeDimension: 'daily',
  sentimentModel: 'random_forest',
  sentimentTrendTimeDimension: 'daily',
  sentimentTrendModel: 'random_forest',
  minKeywordCount: 3,
  minRegionCount: 3
})

const hasSelectedContent = computed(() => {
  return reportConfig.value.quantityTrend || 
         reportConfig.value.sentimentAnalysis ||
         reportConfig.value.sentimentTrend ||
         reportConfig.value.wordCloud || 
         reportConfig.value.regionDistribution
})

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

const handleReset = () => {
  selectedVideoId.value = null
  selectedVideo.value = null
  searchKeyword.value = ''
  filteredVideos.value = []
  showDropdown.value = false
  reportData.value = null
  error.value = ''
  reportConfig.value = {
    quantityTrend: false,
    sentimentAnalysis: false,
    sentimentTrend: false,
    wordCloud: false,
    regionDistribution: false,
    trendTimeDimension: 'daily',
    sentimentModel: 'random_forest',
    sentimentTrendTimeDimension: 'daily',
    sentimentTrendModel: 'random_forest',
    minKeywordCount: 3,
    minRegionCount: 3
  }
}

const handleGenerateReport = async () => {
  if (!selectedVideoId.value || !hasSelectedContent.value) {
    return
  }

  loading.value = true
  error.value = ''
  reportData.value = null

  try {
    const response = await fetch('http://localhost:5000/api/generate-report', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        videoId: selectedVideo.value.video_id,
        title: selectedVideo.value.title,
        config: reportConfig.value
      })
    })

    const data = await response.json()

    if (data.success) {
      reportData.value = data.report
    } else {
      error.value = data.message || '生成报告失败'
    }
  } catch (err) {
    console.error('生成报告失败:', err)
    error.value = '生成报告失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}

const handleDownload = () => {
  console.log('开始下载HTML报告')
  console.log('报告数据是否存在:', !!reportData.value)
  
  if (!reportData.value) {
    console.error('报告数据为空')
    return
  }
  
  const blob = new Blob([reportData.value], { type: 'text/html' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `分析报告_${selectedVideo.value.title || '视频'}.html`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  console.log('HTML下载完成')
}
</script>

<style scoped>
.export-report-wrapper {
  padding: 2rem;
  background-color: #f5f7fa;
  min-height: 100vh;
  margin-left: 16rem;
}

.export-report-container {
  width: 100%;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.export-report-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 2rem;
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
  background-color: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-height: 300px;
  overflow-y: auto;
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

.format-select {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9rem;
  background-color: white;
  cursor: pointer;
  transition: border-color 0.2s;
}

.format-select:hover {
  border-color: #3b82f6;
}

.format-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
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

.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
  color: #6b7280;
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  background-color: #f9fafb;
}

.placeholder i {
  font-size: 3rem;
  color: #3b82f6;
}

.report-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.content-selection h3,
.filter-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  padding: 1.5rem;
  background-color: #f9fafb;
  border-radius: 8px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.75rem;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.checkbox-item:hover {
  background-color: #f3f4f6;
}

.checkbox-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.checkbox-item span {
  font-size: 0.95rem;
  color: #374151;
}

.filter-section {
  padding: 1.5rem;
  background-color: #f9fafb;
  border-radius: 8px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.filter-group label {
  font-weight: 500;
  color: #374151;
  white-space: nowrap;
  min-width: 120px;
}

.filter-group select,
.filter-group input[type="number"] {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9rem;
  background-color: white;
  transition: border-color 0.2s;
}

.filter-group select:hover,
.filter-group input[type="number"]:hover {
  border-color: #6366f1;
}

.filter-group select:focus,
.filter-group input[type="number"]:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.filter-subsection {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: white;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.filter-subsection h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #6366f1;
}

.filter-subsection .filter-group {
  margin-bottom: 0.5rem;
}

.filter-subsection .filter-group:last-child {
  margin-bottom: 0;
}

.generate-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading,
.error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
  color: #6b7280;
}

.loading i,
.error i {
  font-size: 3rem;
}

.loading span,
.error span {
  font-size: 1rem;
}

.error {
  color: #ef4444;
}

.report-result {
  padding: 1.5rem;
  background-color: #f9fafb;
  border-radius: 8px;
}

.report-result h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.report-content-text {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  max-height: 600px;
  overflow-y: auto;
  line-height: 1.8;
  color: #374151;
}

.report-content-text h1 {
  font-size: 1.5rem;
  color: #1f2937;
  margin-bottom: 1rem;
}

.report-content-text h2 {
  font-size: 1.25rem;
  color: #374151;
  margin-bottom: 0.75rem;
}

.report-content-text h3 {
  font-size: 1.1rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.report-content-text p {
  margin-bottom: 1rem;
}

.report-content-text ul {
  margin-bottom: 1rem;
  padding-left: 1.5rem;
}

.report-content-text li {
  margin-bottom: 0.5rem;
}

.download-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 2rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
  max-width: 400px;
  margin: 2rem auto 0;
}

.download-btn:hover {
  background-color: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}
</style>
