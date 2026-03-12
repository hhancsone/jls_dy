<template>
  <div class="videos-wrapper">
    <div class="videos-container">
      <div class="videos-header">
        <h1 class="videos-title">视频管理</h1>
        <div class="header-actions">
          <div class="crawl-section">
            <div class="flex">
              <input 
                type="text" 
                v-model="videoUrl"
                placeholder="https://www.douyin.com/video/..."
                class="flex-1 border border-gray-300 rounded px-4 py-2 focus:outline-none"
                :disabled="isCrawling"
              >
              <button @click="crawlComments" class="btn-primary rounded-none" :disabled="isCrawling">
                <i v-if="isCrawling" class="fa fa-spinner fa-spin mr-2"></i>
                {{ isCrawling ? '爬取中...' : '开始爬取' }}
              </button>
            </div>
          </div>
          <div class="search-bar">
            <div class="search-input-wrapper">
              <i class="fa fa-search search-icon"></i>
              <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="搜索视频标题或链接..." 
                class="search-input"
              >
            </div>
            <button @click="handleSearch" class="search-button">
              <i class="fa fa-search"></i>
              搜索
            </button>
            <button @click="exportToExcel" class="export-button" :disabled="videos.length === 0">
              <i class="fa fa-file-excel-o"></i>
              导出Excel
            </button>
            <button @click="showBatchCrawlModal = true" class="batch-crawl-button">
              <i class="fa fa-list-ol"></i>
              多项爬取
            </button>
          </div>
        </div>
      </div>

      <div class="videos-table-container">
        <table class="videos-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>视频标题</th>
              <th>作者名称</th>
              <th>视频链接</th>
              <th>评论数</th>
              <th>创建人员</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="video in paginatedVideos" :key="video.id">
              <td>{{ video.id }}</td>
              <td :title="video.title">{{ truncateTitle(video.title) }}</td>
              <td>{{ video.author_name || '-' }}</td>
              <td>
                <a :href="video.video_url" target="_blank" class="video-link">
                  {{ truncateUrl(video.video_url) }}
                </a>
              </td>
              <td>{{ video.comment_count || 0 }}</td>
              <td>{{ video.created_by || '管理员' }}</td>
              <td>{{ formatDate(video.created_at) }}</td>
              <td class="actions">
                <button @click="viewDetails(video)" class="action-button view">
                  <i class="fa fa-eye"></i>
                </button>
                <button @click="downloadCsv(video)" class="action-button download">
                  <i class="fa fa-download"></i>
                </button>
                <button @click="deleteVideo(video.id)" class="action-button delete">
                  <i class="fa fa-trash"></i>
                </button>
              </td>
            </tr>
            <tr v-if="paginatedVideos.length === 0">
              <td colspan="8" class="no-data">
                暂无视频数据
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="totalPages > 1" class="pagination">
        <button 
          @click="changePage(currentPage - 1)" 
          :disabled="currentPage === 1"
          class="pagination-button"
        >
          <i class="fa fa-chevron-left"></i>
        </button>
        <span 
          v-for="page in totalPages" 
          :key="page"
          @click="changePage(page)"
          :class="['pagination-number', { active: currentPage === page }]"
        >
          {{ page }}
        </span>
        <button 
          @click="changePage(currentPage + 1)" 
          :disabled="currentPage === totalPages"
          class="pagination-button"
        >
          <i class="fa fa-chevron-right"></i>
        </button>
      </div>
    </div>

    <div v-if="showDetailModal" class="modal-overlay" @click="showDetailModal = false">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h2>视频详情</h2>
          <button @click="showDetailModal = false" class="modal-close">
            <i class="fa fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="detail-item">
            <label>视频标题：</label>
            <span>{{ selectedVideo?.title || '-' }}</span>
          </div>
          <div class="detail-item">
            <label>作者名称：</label>
            <span>{{ selectedVideo?.author_name || '-' }}</span>
          </div>
          <div class="detail-item">
            <label>视频链接：</label>
            <a :href="selectedVideo?.video_url" target="_blank">{{ selectedVideo?.video_url }}</a>
          </div>
          <div class="detail-item">
            <label>评论数量：</label>
            <span>{{ selectedVideo?.comment_count || 0 }}</span>
          </div>
          <div class="detail-item">
            <label>创建人员：</label>
            <span>{{ selectedVideo?.created_by || '管理员' }}</span>
          </div>
          <div class="detail-item">
            <label>视频标签：</label>
            <div v-if="selectedVideo?.tags" class="video-tags">
              <span v-for="(tag, index) in selectedVideo.tags.split(',')" :key="index" class="tag">
                {{ tag }}
              </span>
            </div>
            <span v-else>-</span>
          </div>
          <div class="detail-item">
            <label>状态：</label>
            <span :class="['status-badge', selectedVideo?.status === 1 ? 'active' : 'inactive']">
              {{ selectedVideo?.status === 1 ? '正常' : '禁用' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showBatchCrawlModal" class="modal-overlay" @click.self="showBatchCrawlModal = false">
      <div class="modal-content batch-crawl-modal">
        <div class="modal-header">
          <h2>多项爬取</h2>
          <button @click="showBatchCrawlModal = false" class="modal-close">
            <i class="fa fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="batch-urls">
            <div class="url-inputs">
              <div 
                v-for="(url, index) in batchUrls" 
                :key="index" 
                class="url-input-item"
              >
                <input 
                  type="text" 
                  v-model="batchUrls[index]"
                  :placeholder="`视频链接 ${index + 1}`"
                  class="url-input"
                  :disabled="isBatchCrawling"
                >
                <button 
                  v-if="batchUrls.length > 1"
                  @click="removeUrlInput(index)" 
                  class="remove-url-btn"
                  :disabled="isBatchCrawling"
                >
                  <i class="fa fa-times"></i>
                </button>
              </div>
            </div>
            <button @click="addUrlInput" class="add-url-btn" :disabled="isBatchCrawling">
              <i class="fa fa-plus"></i>
              添加链接
            </button>
          </div>
          <div class="batch-progress" v-if="isBatchCrawling">
            <div class="progress-info">
              <span>正在爬取: {{ currentCrawlIndex + 1 }} / {{ batchUrls.length }}</span>
              <span>{{ crawlProgress }}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: crawlProgress + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showBatchCrawlModal = false" class="cancel-btn" :disabled="isBatchCrawling">
            取消
          </button>
          <button @click="startBatchCrawl" class="confirm-btn" :disabled="isBatchCrawling || !hasValidUrls">
            <i v-if="isBatchCrawling" class="fa fa-spinner fa-spin mr-2"></i>
            {{ isBatchCrawling ? '爬取中...' : '开始爬取' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { videoApi } from '../../utils/api.js'
import * as XLSX from 'xlsx'

const videos = ref([])
const searchQuery = ref('')
const videoUrl = ref('')
const isCrawling = ref(false)
const currentPage = ref(1)
const pageSize = 5
const showDetailModal = ref(false)
const selectedVideo = ref(null)
const showBatchCrawlModal = ref(false)
const batchUrls = ref(['', '', ''])
const isBatchCrawling = ref(false)
const currentCrawlIndex = ref(0)
const crawlProgress = ref(0)

const hasValidUrls = computed(() => {
  return batchUrls.value.some(url => url && url.trim())
})

const filteredVideos = computed(() => {
  return videos.value
})

const totalPages = computed(() => {
  return Math.ceil(filteredVideos.value.length / pageSize)
})

const paginatedVideos = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize
  const endIndex = startIndex + pageSize
  return filteredVideos.value.slice(startIndex, endIndex)
})

const fetchVideos = async () => {
  try {
    console.log('开始获取视频列表...')
    const data = await videoApi.getVideos(searchQuery.value)
    console.log('获取到的视频数据:', data)
    if (data.success) {
      videos.value = data.videos
      console.log('视频列表更新成功，共', data.videos.length, '个视频')
    }
  } catch (error) {
    console.error('获取视频列表失败:', error)
  }
}

const handleSearch = async () => {
  console.log('点击搜索按钮，搜索关键词:', searchQuery.value)
  currentPage.value = 1
  await fetchVideos()
}

const crawlComments = async () => {
  if (!videoUrl.value) {
    alert('请输入视频链接')
    return
  }

  isCrawling.value = true

  try {
    const data = await videoApi.crawlComments(videoUrl.value)
    if (data.success) {
      alert(`爬取成功，共获取 ${data.comments.length} 条评论`)
      videoUrl.value = ''
      fetchVideos()
    } else {
      alert(data.message || '爬取失败')
    }
  } catch (error) {
    console.error('爬取评论失败:', error)
    alert('爬取评论失败，请检查网络连接')
  } finally {
    isCrawling.value = false
  }
}

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const deleteVideo = async (id) => {
  if (!confirm('确定要删除这个视频吗？')) {
    return
  }

  try {
    const data = await videoApi.deleteVideo(id)
    if (data.success) {
      alert('删除成功')
      fetchVideos()
    } else {
      alert(data.message || '删除失败')
    }
  } catch (error) {
    console.error('删除视频失败:', error)
    alert('删除失败')
  }
}

const viewDetails = (video) => {
  selectedVideo.value = video
  showDetailModal.value = true
}

const downloadCsv = async (video) => {
  try {
    const downloadUrl = videoApi.downloadCsv(video.id)
    const userStr = localStorage.getItem('user')
    const user = userStr ? JSON.parse(userStr) : {}
    
    const headers = {}
    if (user.id) {
      headers['x-user-id'] = user.id
    }
    
    const response = await fetch(downloadUrl, { headers })
    
    if (!response.ok) {
      try {
        const data = await response.json()
        alert(data.message || '下载失败')
      } catch {
        alert('下载失败')
      }
      return
    }
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    
    const safeTitle = video.title ? video.title.replace(/[^\w\s\u4e00-\u9fa5-]/g, '') : 'video'
    a.download = `${safeTitle}.csv`
    
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('下载CSV失败:', error)
    alert('下载失败')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const truncateUrl = (url) => {
  if (!url) return '-'
  if (url.length > 40) {
    return url.substring(0, 40) + '...'
  }
  return url
}

const truncateTitle = (title) => {
  if (!title) return '-'
  if (title.length > 50) {
    return title.substring(0, 50) + '...'
  }
  return title
}

const exportToExcel = () => {
  if (videos.value.length === 0) {
    alert('暂无数据可导出')
    return
  }

  try {
    const exportData = videos.value.map(video => ({
      'ID': video.id,
      '视频标题': video.title || '-',
      '作者名称': video.author_name || '-',
      '视频链接': video.video_url || '-',
      '评论数': video.comment_count || 0,
      '创建人员': video.created_by || '管理员',
      '创建时间': formatDate(video.created_at)
    }))

    const ws = XLSX.utils.json_to_sheet(exportData)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '视频列表')

    const fileName = `视频列表_${new Date().toLocaleDateString('zh-CN').replace(/\//g, '-')}.xlsx`
    XLSX.writeFile(wb, fileName)
  } catch (error) {
    console.error('导出Excel失败:', error)
    alert('导出Excel失败')
  }
}

const addUrlInput = () => {
  batchUrls.value.push('')
}

const removeUrlInput = (index) => {
  batchUrls.value.splice(index, 1)
}

const startBatchCrawl = async () => {
  const validUrls = batchUrls.value.filter(url => url && url.trim())
  
  if (validUrls.length === 0) {
    alert('请至少输入一个有效的视频链接')
    return
  }

  isBatchCrawling.value = true
  currentCrawlIndex.value = 0
  crawlProgress.value = 0

  const results = {
    success: 0,
    failed: 0,
    errors: []
  }

  for (let i = 0; i < validUrls.length; i++) {
    currentCrawlIndex.value = i
    crawlProgress.value = Math.round((i / validUrls.length) * 100)

    try {
      const data = await videoApi.crawlComments(validUrls[i])
      if (data.success) {
        results.success++
      } else {
        results.failed++
        results.errors.push({ url: validUrls[i], message: data.message || '爬取失败' })
      }
    } catch (error) {
      results.failed++
      results.errors.push({ url: validUrls[i], message: error.message || '网络错误' })
    }

    await new Promise(resolve => setTimeout(resolve, 500))
  }

  crawlProgress.value = 100
  await fetchVideos()

  alert(`批量爬取完成！\n成功：${results.success} 条\n失败：${results.failed} 条`)

  isBatchCrawling.value = false
  batchUrls.value = ['', '', '']
}

onMounted(() => {
  fetchVideos()
})
</script>

<style scoped>
.videos-wrapper {
  padding: 2rem;
  background-color: #f5f7fa;
  min-height: 100vh;
  width: calc(100% - 16rem);
  margin-left: 16rem;
}

.videos-container {
  width: 100%;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.videos-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.videos-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.crawl-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.search-bar {
  display: flex;
  gap: 0.5rem;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  color: #9ca3af;
}

.search-input {
  padding-left: 2.5rem;
  padding-right: 1rem;
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  width: 300px;
  font-size: 0.875rem;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-button {
  padding: 0.5rem 1rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.search-button:hover {
  background-color: #2563eb;
}

.export-button {
  padding: 0.5rem 1rem;
  background-color: #10b981;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.export-button:hover:not(:disabled) {
  background-color: #059669;
}

.export-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.videos-table-container {
  overflow-x: auto;
}

.videos-table {
  width: 100%;
  border-collapse: collapse;
}

.videos-table th {
  background-color: #f9fafb;
  padding: 0.75rem 0.5rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.75rem;
  color: #6b7280;
  border-bottom: 1px solid #e5e7eb;
}

.videos-table th:nth-child(2) {
  max-width: 150px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.videos-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e5e7eb;
  font-size: 0.875rem;
  color: #374151;
}

.videos-table td[title] {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: help;
}

.videos-table td[title]:hover {
  color: #3b82f6;
}

.video-link {
  color: #3b82f6;
  text-decoration: none;
}

.video-link:hover {
  text-decoration: underline;
}

.video-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.tag {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  background-color: #e0f2fe;
  color: #0369a1;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.action-button {
  padding: 0.375rem 0.75rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.action-button.view {
  background-color: #3b82f6;
  color: white;
}

.action-button.view:hover {
  background-color: #2563eb;
}

.action-button.download {
  background-color: #10b981;
  color: white;
}

.action-button.download:hover {
  background-color: #059669;
}

.action-button.delete {
  background-color: #ef4444;
  color: white;
}

.action-button.delete:hover {
  background-color: #dc2626;
}

.no-data {
  text-align: center;
  padding: 2rem;
  color: #9ca3af;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.pagination-button {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  background-color: white;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.pagination-button:hover:not(:disabled) {
  background-color: #f3f4f6;
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-number {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  background-color: white;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.pagination-number:hover {
  background-color: #f3f4f6;
}

.pagination-number.active {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 0.75rem;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content.large {
  max-width: 700px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.modal-close {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  color: #6b7280;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.form-group input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.form-group input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.btn-secondary {
  padding: 0.5rem 1rem;
  background-color: white;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #374151;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #f3f4f6;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  padding: 0.5rem 1rem;
  background-color: #3b82f6;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.fa-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.mr-2 {
  margin-right: 0.5rem;
}

.flex {
  display: flex;
}

.flex-1 {
  flex: 1;
}

.border {
  border: 1px solid;
}

.border-gray-300 {
  border-color: #d1d5db;
}

.rounded {
  border-radius: 0.5rem;
}

.px-4 {
  padding-left: 1rem;
  padding-right: 1rem;
}

.py-2 {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}

.focus\:outline-none:focus {
  outline: none;
}

.block {
  display: block;
}

.batch-crawl-button {
  padding: 0.75rem 1.5rem;
  background-color: #8b5cf6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.batch-crawl-button:hover:not(:disabled) {
  background-color: #7c3aed;
}

.batch-crawl-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.batch-crawl-modal {
  max-width: 600px;
}

.batch-urls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.url-inputs {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.url-input-item {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.url-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
}

.url-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.url-input:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
}

.remove-url-btn {
  padding: 0.5rem;
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.remove-url-btn:hover:not(:disabled) {
  background-color: #dc2626;
}

.remove-url-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.add-url-btn {
  padding: 0.5rem 1rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  align-self: flex-start;
}

.add-url-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.add-url-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.batch-progress {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f9fafb;
  border-radius: 0.5rem;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #3b82f6;
  transition: width 0.3s ease;
}

.cancel-btn {
  padding: 0.5rem 1rem;
  background-color: #f3f4f6;
  color: #374151;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.cancel-btn:hover:not(:disabled) {
  background-color: #e5e7eb;
}

.cancel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.confirm-btn {
  padding: 0.5rem 1rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.confirm-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.text-sm {
  font-size: 0.875rem;
}

.font-medium {
  font-weight: 500;
}

.text-gray-700 {
  color: #374151;
}

.mb-1 {
  margin-bottom: 0.25rem;
}

.detail-item {
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
}

.detail-item label {
  font-weight: 500;
  color: #374151;
  min-width: 100px;
}

.detail-item span,
.detail-item a {
  color: #6b7280;
}

.detail-item a {
  color: #3b82f6;
  text-decoration: none;
}

.detail-item a:hover {
  text-decoration: underline;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.active {
  background-color: #d1fae5;
  color: #10b981;
}

.status-badge.inactive {
  background-color: #fee2e2;
  color: #ef4444;
}

.mr-2 {
  margin-right: 0.5rem;
}
</style>
