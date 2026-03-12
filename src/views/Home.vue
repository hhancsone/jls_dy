<template>
  <div class="home-wrapper">
    <div class="home-container">
      <section class="intro-section bg-white rounded-xl shadow-sm p-6 mb-6">
        <h2 class="text-xl font-semibold text-dark mb-4 flex items-center">
          <i class="fa fa-info-circle mr-2 text-primary"></i>项目介绍
        </h2>
        <p class="text-gray-700 leading-relaxed intro-text">
            抖音评论情感分析系统是一个基于机器学习的智能分析平台，能够自动爬取抖音视频评论，
          并对评论内容进行情感分析、关键词提取、地区分布统计等多维度分析。
          系统支持多种机器学习模型，包括随机森林、朴素贝叶斯、逻辑回归、支持向量机和梯度提升等，
          帮助用户深入了解用户评论的情感倾向和内容特征。
        </p>
      </section>

      <section class="quick-start-section bg-white rounded-xl shadow-sm p-6 mb-6">
        <h2 class="text-xl font-semibold text-dark mb-4 flex items-center">
          <i class="fa fa-rocket mr-2 text-primary"></i>快速开始
        </h2>
        <div class="flex gap-4">
          <div class="flex-1">
            <div class="flex">
              <input 
                type="text" 
                id="video-url" 
                v-model="videoUrl"
                placeholder="https://www.douyin.com/video/..."
                class="flex-1 border border-gray-300 rounded px-4 py-2 focus:outline-none"
                :disabled="loading"
              >
              <button @click="fetchComments" class="btn-primary rounded-none" :disabled="loading">
                <i class="fa fa-arrow-right"></i>{{ loading ? '爬取中...' : '开始爬取' }}
              </button>
            </div>
          </div>
        </div>
      </section>

      <section class="stats-section grid grid-cols-2 gap-4 mb-6">
        <div class="stat-card bg-white rounded-xl shadow-sm p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-700">已分析视频</h3>
            <i class="fa fa-video-camera text-3xl text-primary"></i>
          </div>
          <p class="text-4xl font-bold text-primary">{{ totalVideos }}</p>
          <p class="text-sm text-gray-500 mt-2">个视频</p>
        </div>
        <div class="stat-card bg-white rounded-xl shadow-sm p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-700">总人数</h3>
            <i class="fa fa-users text-3xl text-secondary"></i>
          </div>
          <p class="text-4xl font-bold text-secondary">{{ totalUsers }}</p>
          <p class="text-sm text-gray-500 mt-2">人</p>
        </div>
      </section>

      <section class="quick-links-section grid grid-cols-3 gap-4 mb-6">
        <div class="link-card bg-white rounded-xl shadow-sm p-6 cursor-pointer hover:shadow-md transition-shadow" @click="goToAnalysis">
          <div class="flex items-center justify-center mb-3" @click.stop>
            <div class="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center">
              <i class="fa fa-heart text-3xl text-primary"></i>
            </div>
          </div>
          <h3 class="text-lg font-semibold text-center text-gray-700">情感分析</h3>
          <p class="text-sm text-center text-gray-500 mt-2">查看评论情感分布</p>
        </div>
        <div class="link-card bg-white rounded-xl shadow-sm p-6 cursor-pointer hover:shadow-md transition-shadow" @click="goToExport">
          <div class="flex items-center justify-center mb-3" @click.stop>
            <div class="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center">
              <i class="fa fa-file-text text-3xl text-secondary"></i>
            </div>
          </div>
          <h3 class="text-lg font-semibold text-center text-gray-700">导出报告</h3>
          <p class="text-sm text-center text-gray-500 mt-2">生成分析报告</p>
        </div>
        <div class="link-card bg-white rounded-xl shadow-sm p-6 cursor-pointer hover:shadow-md transition-shadow" @click="goToVideos">
          <div class="flex items-center justify-center mb-3" @click.stop>
            <div class="w-16 h-16 rounded-full bg-purple-100 flex items-center justify-center">
              <i class="fa fa-video-camera text-3xl text-purple-600"></i>
            </div>
          </div>
          <h3 class="text-lg font-semibold text-center text-gray-700">视频管理</h3>
          <p class="text-sm text-center text-gray-500 mt-2">管理已分析视频</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { videoApi, userApi } from '../utils/api.js'

const router = useRouter()
const videoUrl = ref('')
const loading = ref(false)
const totalVideos = ref(0)
const totalUsers = ref(0)

const fetchComments = async () => {
  if (!videoUrl.value.trim()) {
    alert('请输入有效的抖音视频链接')
    return
  }

  loading.value = true

  try {
    const data = await videoApi.crawlComments(videoUrl.value)

    if (data.success) {
      alert(`成功爬取 ${data.comments.length} 条评论，CSV文件已生成`)
      videoUrl.value = ''
      await loadStats()
    } else {
      alert(data.message || '爬取失败')
    }
  } catch (error) {
    console.error('爬取评论失败:', error)
    alert('爬取评论失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const videosData = await videoApi.getVideos()
    if (videosData.success) {
      totalVideos.value = videosData.videos.length
    }

    const usersData = await userApi.getUsers()
    if (usersData.success) {
      totalUsers.value = usersData.users.length
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const goToAnalysis = () => {
  router.push('/overview')
}

const goToExport = () => {
  router.push('/export-report')
}

const goToVideos = () => {
  router.push('/videos')
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.home-wrapper {
  padding: 2rem;
  background-color: #f5f7fa;
  min-height: 100vh;
  margin-left: 16rem;
}

.home-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.quick-start-section,
.stats-section,
.quick-links-section {
  width: 100%;
}

.stat-card {
  text-align: center;
}

.link-card {
  text-align: center;
  transition: all 0.3s ease;
  pointer-events: auto;
}

.link-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

input {
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
}

input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.grid {
  display: grid;
}

.grid-cols-2 {
  grid-template-columns: repeat(2, 1fr);
}

.grid-cols-3 {
  grid-template-columns: repeat(3, 1fr);
}

.gap-4 {
  gap: 1rem;
}

.text-3xl {
  font-size: 1.875rem;
  line-height: 2.25rem;
}

.text-4xl {
  font-size: 2.25rem;
  line-height: 2.5rem;
}

.text-primary {
  color: #3b82f6;
}

.text-secondary {
  color: #10b981;
}

.text-purple-600 {
  color: #9333ea;
}

.bg-blue-100 {
  background-color: #dbeafe;
}

.bg-green-100 {
  background-color: #d1fae5;
}

.bg-purple-100 {
  background-color: #e9d5ff;
}

.transition-shadow {
  transition: box-shadow 0.3s ease;
}

.hover\:shadow-md:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.cursor-pointer {
  cursor: pointer;
}

.flex {
  display: flex;
}

.flex-1 {
  flex: 1;
}

.items-center {
  align-items: center;
}

.justify-between {
  justify-content: space-between;
}

.justify-center {
  justify-content: center;
}

.mr-2 {
  margin-right: 0.5rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mb-3 {
  margin-bottom: 0.75rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

.mb-6 {
  margin-bottom: 1.5rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

.p-6 {
  padding: 1.5rem;
}

.p-8 {
  padding: 2rem;
}

.rounded {
  border-radius: 0.5rem;
}

.rounded-xl {
  border-radius: 0.75rem;
}

.shadow-sm {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.bg-white {
  background-color: white;
}

.text-white {
  color: white;
}

.text-dark {
  color: #1f2937;
}

.text-gray-500 {
  color: #6b7280;
}

.text-gray-700 {
  color: #374151;
}

.text-sm {
  font-size: 0.875rem;
}

.text-lg {
  font-size: 1.125rem;
}

.text-xl {
  font-size: 1.25rem;
}

.font-semibold {
  font-weight: 600;
}

.font-bold {
  font-weight: 700;
}

.w-16 {
  width: 4rem;
}

.h-16 {
  height: 4rem;
}

.rounded-full {
  border-radius: 9999px;
}

.text-3xl {
  font-size: 1.875rem;
}

.border {
  border: 1px solid;
}

.border-gray-300 {
  border-color: #d1d5db;
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

.btn-primary {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.rounded-none {
  border-radius: 0;
}

.intro-text {
  line-height: 2;
  text-indent: 2em;
  margin: 1rem 0;
}
</style>
