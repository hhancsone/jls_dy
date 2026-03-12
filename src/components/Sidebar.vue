<template>
  <aside class="sidebar-container">
    <div class="sidebar-user-info">
      <div class="sidebar-avatar">
        <i class="fa fa-user"></i>
      </div>
      <div class="sidebar-user-details">
        <h3>{{ config.user.name }}</h3>
        <p class="user-role">{{ config.user.role }}</p>
      </div>
    </div>

    <div class="sidebar-nav-title">
      <h4>{{ config.navigation.title }}</h4>
    </div>

    <nav class="sidebar-nav">
      <ul>
        <li v-for="item in config.navigation.items" :key="item.id" class="sidebar-nav-item">
          <button 
            v-if="item.id !== 'users' || isAdmin"
            @click="setActiveNav(item.id)"
            :class="['sidebar-nav-button', { active: item.active }]"
          >
            <i :class="['fa', item.icon]"></i>
            <span>{{ item.label }}</span>
          </button>
        </li>
      </ul>
    </nav>
  </aside>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const config = ref({
  user: {
    name: '未登录',
    username: 'Guest',
    role: '访客',
    avatar: 'https://via.placeholder.com/150'
  },
  navigation: {
    title: '导航栏',
    items: [
      { id: 'home', icon: 'fa-home', label: '首页', active: true, path: '/' },
      { id: 'users', icon: 'fa-users', label: '用户管理', active: false, path: '/users' },
      { id: 'videos', icon: 'fa-video-camera', label: '视频管理', active: false, path: '/videos' },
      { id: 'sentiment-trend', icon: 'fa-line-chart', label: '数量趋势', active: false, path: '/sentiment-trend' },
      { id: 'sentiment-distribution', icon: 'fa-pie-chart', label: '情感分布分析', active: false, path: '/overview' },
      { id: 'sentiment-trend-analysis', icon: 'fa-area-chart', label: '情感趋势分析', active: false, path: '/sentiment-trend-analysis' },
      { id: 'comments', icon: 'fa-comments', label: '评论详情', active: false, path: '/comments' },
      { id: 'comment-wordcloud', icon: 'fa-tags', label: '评论词云图', active: false, path: '/keywords' },
      { id: 'region-distribution', icon: 'fa-map-marker', label: '分布地区', active: false, path: '/region-distribution' },
      { id: 'export', icon: 'fa-download', label: '导出报告', active: false, path: '/export-report' }
    ]
  },
  quickStart: {
    title: '快速入门',
    buttonText: '跳转首页',
    buttonIcon: 'fa-play-circle'
  }
})

const isAdmin = computed(() => {
  return config.value.user.role === '管理员'
})

const loadUserInfo = async () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    const user = JSON.parse(userStr)
    try {
      const response = await fetch(`http://localhost:3001/api/user/${user.id}`)
      const data = await response.json()
      if (data.success) {
        config.value.user.name = data.user.username || data.user.name || '用户'
        config.value.user.username = data.user.username || 'User'
        config.value.user.role = data.user.role === 'admin' ? '管理员' : '普通用户'
        config.value.user.avatar = data.user.avatar || 'https://via.placeholder.com/150'
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      config.value.user.name = user.username || user.name || '用户'
      config.value.user.username = user.username || 'User'
      config.value.user.role = user.role === 'admin' ? '管理员' : '普通用户'
      config.value.user.avatar = user.avatar || 'https://via.placeholder.com/150'
    }
  }
}

const setActiveNav = (id) => {
  config.value.navigation.items.forEach(item => {
    item.active = item.id === id
    if (item.id === id && item.path) {
      router.push(item.path)
    }
  })
}

const updateActiveNavByRoute = () => {
  const currentPath = route.path
  config.value.navigation.items.forEach(item => {
    item.active = item.path === currentPath
  })
}

watch(() => route.path, () => {
  updateActiveNavByRoute()
})

onMounted(() => {
  loadUserInfo()
  updateActiveNavByRoute()
})
</script>

<style scoped>
.sidebar-container {
  position: fixed;
  left: 0;
  top: 64px;
  bottom: 0;
  width: 16rem;
  background-color: white;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  padding: 1rem;
  overflow-y: auto;
  z-index: 10;
}

.sidebar-user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  margin-bottom: 1.5rem;
}

.sidebar-avatar {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  background-color: #3B82F6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-avatar i {
  font-size: 1.5rem;
  color: white;
}

.sidebar-user-details h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.sidebar-user-details p {
  font-size: 0.875rem;
  color: #6b7280;
}

.user-role {
  font-size: 0.75rem;
  color: #9CA3AF;
  margin-top: 0.25rem;
}

.sidebar-nav-title h4 {
  font-size: 0.75rem;
  font-weight: 600;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
}

.sidebar-nav {
  margin-bottom: 1.5rem;
}

.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-nav-item {
  margin-bottom: 0.25rem;
}

.sidebar-nav-button {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  background: none;
  transition: all 0.2s ease;
  color: #4b5563;
}

.sidebar-nav-button:hover {
  background-color: #f3f4f6;
}

.sidebar-nav-button.active {
  background-color: #eff6ff;
  color: #3b82f6;
}

.sidebar-quick-start {
  padding: 1rem;
  background-color: #f9fafb;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.sidebar-quick-start h3 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.sidebar-quick-start p {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.75rem;
  line-height: 1.5;
}

.sidebar-quick-start button {
  width: 100%;
  padding: 0.5rem 0.75rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.sidebar-quick-start button:hover {
  background-color: #2563eb;
}
</style>
