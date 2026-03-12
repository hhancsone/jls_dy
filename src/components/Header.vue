<template>
  <header class="header-container">
    <div class="header-logo">
      <i :class="['fa', config.logoIcon, 'text-primary', 'text-2xl']"></i>
      <h1 class="header-title">{{ config.title }}</h1>
    </div>
    <div class="header-actions">
      <button @click="showProfileModal = true" class="p-2 rounded-full hover:bg-gray-100">
        <i :class="['fa', config.profileButtonIcon, 'text-gray-600']"></i>
      </button>
      <button @click="logout" class="p-2 rounded-full hover:bg-gray-100">
        <i :class="['fa', config.logoutButtonIcon, 'text-gray-600']"></i>
      </button>
    </div>

    <div v-if="showProfileModal" class="modal-overlay" @click.self="showProfileModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2>个人信息</h2>
          <button @click="showProfileModal = false" class="modal-close">
            <i class="fa fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="profile-info">
            <div class="info-item">
              <label>用户名：</label>
              <span>{{ userInfo.username }}</span>
            </div>
            <div class="info-item">
              <label>邮箱：</label>
              <span>{{ userInfo.email || '-' }}</span>
            </div>
            <div class="info-item">
              <label>角色：</label>
              <span>{{ userInfo.role === 'admin' ? '管理员' : '普通用户' }}</span>
            </div>
          </div>

          <div class="password-section">
            <h3>修改密码</h3>
            <form @submit.prevent="handleChangePassword">
              <div class="form-group">
                <label>当前密码 *</label>
                <input 
                  type="password" 
                  v-model="passwordForm.currentPassword" 
                  placeholder="请输入当前密码"
                  required
                >
              </div>
              <div class="form-group">
                <label>新密码 *</label>
                <input 
                  type="password" 
                  v-model="passwordForm.newPassword" 
                  placeholder="请输入新密码（至少6位）"
                  minlength="6"
                  required
                >
              </div>
              <div class="form-group">
                <label>确认新密码 *</label>
                <input 
                  type="password" 
                  v-model="passwordForm.confirmPassword" 
                  placeholder="请再次输入新密码"
                  required
                >
              </div>
              <div class="modal-actions">
                <button type="button" @click="showProfileModal = false" class="btn-secondary">
                  取消
                </button>
                <button type="submit" class="btn-primary" :disabled="passwordLoading">
                  {{ passwordLoading ? '修改中...' : '确认修改' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../utils/api.js'

const router = useRouter()

const config = ref({
  title: '抖音评论情感分析平台',
  logoIcon: 'fa-bar-chart',
  profileButtonIcon: 'fa-user',
  logoutButtonIcon: 'fa-sign-out'
})

const showProfileModal = ref(false)
const userInfo = ref({
  username: '未登录',
  email: '',
  role: 'user'
})
const passwordLoading = ref(false)
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const loadUserInfo = async () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    const user = JSON.parse(userStr)
    userInfo.value = {
      username: user.username || '用户',
      email: user.email || '',
      role: user.role || 'user'
    }
  }
}

const handleChangePassword = async () => {
  if (!passwordForm.value.currentPassword) {
    alert('请输入当前密码')
    return
  }

  if (!passwordForm.value.newPassword || passwordForm.value.newPassword.length < 6) {
    alert('新密码长度至少为6位')
    return
  }

  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    alert('两次输入的密码不一致')
    return
  }

  passwordLoading.value = true

  try {
    const data = await authApi.changePassword({
      currentPassword: passwordForm.value.currentPassword,
      newPassword: passwordForm.value.newPassword
    })

    if (data.success) {
      alert('密码修改成功，请重新登录')
      localStorage.removeItem('user')
      router.push('/login')
    } else {
      alert(data.message || '密码修改失败')
    }
  } catch (error) {
    console.error('修改密码失败:', error)
    alert('修改密码失败，请检查网络连接')
  } finally {
    passwordLoading.value = false
  }
}

const logout = () => {
  if (confirm('确定要退出登录吗？')) {
    localStorage.removeItem('user')
    router.push('/login')
  }
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.header-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: white;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  z-index: 20;
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-actions button {
  padding: 0.5rem;
  border-radius: 9999px;
  border: none;
  background: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.header-actions button:hover {
  background-color: #f3f4f6;
}

.header-actions button i {
  color: #6b7280;
  font-size: 1rem;
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
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
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
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #6b7280;
  cursor: pointer;
  transition: color 0.2s ease;
}

.modal-close:hover {
  color: #374151;
}

.modal-body {
  padding: 1.5rem;
}

.profile-info {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.info-item {
  display: flex;
  margin-bottom: 1rem;
}

.info-item label {
  font-weight: 500;
  color: #374151;
  min-width: 80px;
}

.info-item span {
  color: #6b7280;
}

.password-section h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
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
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background-color: #f3f4f6;
  color: #374151;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-secondary:hover {
  background-color: #e5e7eb;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
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
</style>
