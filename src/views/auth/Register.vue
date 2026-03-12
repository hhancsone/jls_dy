<template>
  <div class="register-container">
    <main class="register-main">
      <div class="register-card">
        <div class="register-header">
          <div class="logo-section">
            <i class="fa fa-bar-chart logo-icon"></i>
            <h1 class="logo-title">抖音评论情感分析平台</h1>
          </div>
          <h2 class="register-title">创建账户</h2>
          <p class="register-subtitle">注册新账户开始使用</p>
        </div>
          
        <form @submit.prevent="handleRegister" class="register-form">
          <div class="form-group">
            <label for="username" class="form-label">用户名 *</label>
            <div class="input-wrapper">
              <i class="fa fa-user input-icon"></i>
              <input 
                type="text" 
                id="username" 
                v-model="formData.username"
                placeholder="请输入用户名"
                class="form-input"
                required
                minlength="3"
                maxlength="50"
              >
            </div>
          </div>
          
          <div class="form-group">
            <label for="email" class="form-label">邮箱地址</label>
            <div class="input-wrapper">
              <i class="fa fa-envelope input-icon"></i>
              <input 
                type="email" 
                id="email" 
                v-model="formData.email"
                placeholder="请输入邮箱地址"
                class="form-input"
              >
            </div>
          </div>
          
          <div class="form-group">
            <label for="password" class="form-label">密码 *</label>
            <div class="input-wrapper">
              <i class="fa fa-lock input-icon"></i>
              <input 
                :type="showPassword ? 'text' : 'password'" 
                id="password" 
                v-model="formData.password"
                placeholder="请输入密码（至少6位）"
                class="form-input"
                required
                minlength="6"
              >
              <button 
                type="button" 
                @click="showPassword = !showPassword"
                class="password-toggle"
              >
                <i :class="['fa', showPassword ? 'fa-eye-slash' : 'fa-eye']"></i>
              </button>
            </div>
          </div>
          
          <div class="form-group">
            <label for="confirmPassword" class="form-label">确认密码 *</label>
            <div class="input-wrapper">
              <i class="fa fa-lock input-icon"></i>
              <input 
                :type="showConfirmPassword ? 'text' : 'password'" 
                id="confirmPassword" 
                v-model="formData.confirmPassword"
                placeholder="请再次输入密码"
                class="form-input"
                required
                minlength="6"
              >
              <button 
                type="button" 
                @click="showConfirmPassword = !showConfirmPassword"
                class="password-toggle"
              >
                <i :class="['fa', showConfirmPassword ? 'fa-eye-slash' : 'fa-eye']"></i>
              </button>
            </div>
          </div>
          
          <div class="form-options">
            <label class="checkbox-label">
              <input type="checkbox" v-model="formData.agreeTerms" required>
              <span>我已阅读并同意 <a href="#" class="terms-link">服务条款</a> 和 <a href="#" class="terms-link">隐私政策</a></span>
            </label>
          </div>
          
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
          
          <button type="submit" class="register-button" :disabled="loading">
            <i class="fa fa-user-plus mr-2" v-if="!loading"></i>
            <i class="fa fa-spinner fa-spin mr-2" v-if="loading"></i>
            {{ loading ? '注册中...' : '注册' }}
          </button>
        </form>
          
        <div class="register-footer">
          <p class="login-text">
            已有账户？
            <router-link to="/login" class="login-link">立即登录</router-link>
          </p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const formData = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeTerms: false
})

const showPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')

const handleRegister = async () => {
  if (formData.value.password !== formData.value.confirmPassword) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }
  
  if (formData.value.password.length < 6) {
    errorMessage.value = '密码长度至少为6位'
    return
  }
  
  if (!formData.value.agreeTerms) {
    errorMessage.value = '请阅读并同意服务条款和隐私政策'
    return
  }
  
  loading.value = true
  errorMessage.value = ''
  
  try {
    const response = await fetch('http://localhost:3001/api/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: formData.value.username,
        email: formData.value.email,
        password: formData.value.password
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      alert('注册成功，请登录')
      router.push('/login')
    } else {
      errorMessage.value = data.message || '注册失败'
    }
  } catch (error) {
    console.error('注册错误:', error)
    errorMessage.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background-color: #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.register-main {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  width: 100%;
}

.register-card {
  background-color: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  padding: 2.5rem;
  width: 100%;
  max-width: 500px;
}

.register-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.logo-icon {
  font-size: 2rem;
  color: #3B82F6;
}

.logo-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1F2937;
  margin: 0;
}

.register-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 0.5rem;
}

.register-subtitle {
  font-size: 0.875rem;
  color: #6B7280;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  color: #9CA3AF;
  font-size: 1rem;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
  border: 1px solid #D1D5DB;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.password-toggle {
  position: absolute;
  right: 1rem;
  background: none;
  border: none;
  cursor: pointer;
  color: #9CA3AF;
  font-size: 1rem;
  padding: 0;
  transition: color 0.2s ease;
}

.password-toggle:hover {
  color: #6B7280;
}

.form-options {
  display: flex;
  align-items: flex-start;
  font-size: 0.875rem;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  color: #4B5563;
  cursor: pointer;
  line-height: 1.5;
}

.checkbox-label input[type="checkbox"] {
  width: 1rem;
  height: 1rem;
  cursor: pointer;
  margin-top: 0.125rem;
}

.terms-link {
  color: #3B82F6;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.terms-link:hover {
  color: #2563EB;
  text-decoration: underline;
}

.error-message {
  background-color: #FEE2E2;
  color: #DC2626;
  padding: 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  text-align: center;
}

.register-button {
  width: 100%;
  padding: 0.875rem;
  background-color: #3B82F6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.register-button:hover {
  background-color: #2563EB;
}

.register-footer {
  margin-top: 2rem;
  text-align: center;
}

.login-text {
  font-size: 0.875rem;
  color: #6B7280;
}

.login-link {
  color: #3B82F6;
  text-decoration: none;
  font-weight: 600;
  margin-left: 0.25rem;
  transition: color 0.2s ease;
}

.login-link:hover {
  color: #2563EB;
  text-decoration: underline;
}

.mr-2 {
  margin-right: 0.5rem;
}
</style>