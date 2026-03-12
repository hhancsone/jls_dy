<template>
  <div class="users-wrapper">
    <div class="users-container">
      <div class="users-header">
        <h1 class="users-title">用户管理</h1>
        <div class="header-actions">
          <div class="search-bar">
            <div class="search-input-wrapper">
              <i class="fa fa-search search-icon"></i>
              <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="搜索用户名或邮箱..." 
                class="search-input"
              >
            </div>
            <button @click="handleSearch" class="search-button">
              <i class="fa fa-search"></i>
              搜索
            </button>
          </div>
          <button @click="showAddModal = true" class="add-button">
            <i class="fa fa-plus mr-2"></i>
            添加用户
          </button>
          <button @click="exportToExcel" class="export-button" :disabled="filteredUsers.length === 0">
            <i class="fa fa-file-excel-o"></i>
            导出Excel
          </button>
          <button @click="downloadTemplate" class="template-button">
            <i class="fa fa-download"></i>
            下载模板
          </button>
          <button @click="triggerImport" class="import-button">
            <i class="fa fa-upload"></i>
            导入Excel
          </button>
          <input 
            type="file" 
            ref="fileInput"
            accept=".xlsx,.xls"
            @change="handleImport"
            style="display: none"
          >
        </div>
      </div>

      <div class="users-table-container">
        <table class="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>用户名</th>
              <th>邮箱</th>
              <th>角色</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in paginatedUsers" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.username }}</td>
              <td>{{ user.email || '-' }}</td>
              <td>
                <span :class="['role-badge', user.role]">
                  {{ user.role === 'admin' ? '管理员' : '普通用户' }}
                </span>
              </td>
              <td>
                <span :class="['status-badge', user.status === 1 ? 'active' : 'inactive']">
                  {{ user.status === 1 ? '正常' : '禁用' }}
                </span>
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td class="actions">
                <button @click="editUser(user)" class="action-button edit">
                  <i class="fa fa-edit"></i>
                </button>
                <button @click="deleteUser(user.id)" class="action-button delete">
                  <i class="fa fa-trash"></i>
                </button>
              </td>
            </tr>
            <tr v-if="paginatedUsers.length === 0">
              <td colspan="7" class="no-data">
                暂无用户数据
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

    <div v-if="showAddModal || showEditModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ showEditModal ? '编辑用户' : '添加用户' }}</h2>
          <button @click="closeModal" class="close-button">
            <i class="fa fa-times"></i>
          </button>
        </div>
        <form @submit.prevent="handleSubmit" class="modal-form">
          <div class="form-group">
            <label>用户名 *</label>
            <input 
              type="text" 
              v-model="formData.username" 
              :disabled="showEditModal"
              required
            >
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input 
              type="email" 
              v-model="formData.email"
            >
          </div>
          <div class="form-group" v-if="!showEditModal">
            <label>密码 *</label>
            <input 
              type="password" 
              v-model="formData.password"
              required
              placeholder="至少6位"
            >
          </div>
          <div class="form-group">
            <label>角色 *</label>
            <select v-model="formData.role" required>
              <option value="user">普通用户</option>
              <option value="admin">管理员</option>
            </select>
          </div>
          <div class="form-group">
            <label>状态 *</label>
            <select v-model="formData.status" required>
              <option :value="1">正常</option>
              <option :value="0">禁用</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeModal" class="cancel-button">
              取消
            </button>
            <button type="submit" class="submit-button" :disabled="loading">
              {{ loading ? '保存中...' : (showEditModal ? '更新' : '添加') }}
            </button>
          </div>
        </form>
      </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { userApi } from '../../utils/api.js'
import * as XLSX from 'xlsx'

const users = ref([])
const searchQuery = ref('')
const showAddModal = ref(false)
const showEditModal = ref(false)
const loading = ref(false)
const currentPage = ref(1)
const pageSize = 5
const isSearching = ref(false)
const searchResults = ref([])
const fileInput = ref(null)
const formData = ref({
  id: null,
  username: '',
  email: '',
  password: '',
  role: 'user',
  status: 1
})

const filteredUsers = computed(() => {
  if (!isSearching.value) return users.value
  return searchResults.value
})

const totalPages = computed(() => {
  return Math.ceil(filteredUsers.value.length / pageSize)
})

const paginatedUsers = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize
  const endIndex = startIndex + pageSize
  return filteredUsers.value.slice(startIndex, endIndex)
})

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const fetchUsers = async () => {
  try {
    const data = await userApi.getUsers()
    if (data.success) {
      users.value = data.users
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
  }
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    isSearching.value = false
    searchResults.value = []
    await fetchUsers()
    return
  }
  
  isSearching.value = true
  currentPage.value = 1
  
  try {
    const data = await userApi.getUsers(searchQuery.value)
    if (data.success) {
      searchResults.value = data.users
    }
  } catch (error) {
    console.error('搜索失败:', error)
    searchResults.value = []
  }
}

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const editUser = (user) => {
  formData.value = {
    id: user.id,
    username: user.username,
    email: user.email,
    password: '',
    role: user.role,
    status: user.status
  }
  showEditModal.value = true
}

const deleteUser = async (userId) => {
  if (!confirm('确定要删除该用户吗？')) return
  
  try {
    const data = await userApi.deleteUser(userId)
    if (data.success) {
      users.value = users.value.filter(u => u.id !== userId)
    }
  } catch (error) {
    console.error('删除用户失败:', error)
  }
}

const handleSubmit = async () => {
  if (!formData.value.username) {
    alert('请输入用户名')
    return
  }
  
  if (!showEditModal.value && formData.value.password && formData.value.password.length < 6) {
    alert('密码长度至少为6位')
    return
  }
  
  loading.value = true
  
  try {
    let data
    if (showEditModal.value) {
      data = await userApi.updateUser(formData.value.id, formData.value)
      if (data.success) {
        const index = users.value.findIndex(u => u.id === formData.value.id)
        if (index !== -1) {
          users.value[index] = data.user
        }
      }
    } else {
      data = await userApi.createUser(formData.value)
      if (data.success) {
        users.value.push(data.user)
      }
    }
    
    if (data.success) {
      closeModal()
    } else {
      alert(data.message || '操作失败')
    }
  } catch (error) {
    console.error('操作失败:', error)
    alert('操作失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  formData.value = {
    id: null,
    username: '',
    email: '',
    password: '',
    role: 'user',
    status: 1
  }
}

const exportToExcel = () => {
  if (filteredUsers.value.length === 0) {
    alert('暂无数据可导出')
    return
  }

  try {
    const exportData = filteredUsers.value.map(user => ({
      'ID': user.id,
      '用户名': user.username,
      '邮箱': user.email || '-',
      '角色': user.role === 'admin' ? '管理员' : '普通用户',
      '状态': user.status === 1 ? '正常' : '禁用',
      '创建时间': formatDate(user.created_at)
    }))

    const ws = XLSX.utils.json_to_sheet(exportData)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '用户列表')

    const fileName = `用户列表_${new Date().toLocaleDateString('zh-CN').replace(/\//g, '-')}.xlsx`
    XLSX.writeFile(wb, fileName)
  } catch (error) {
    console.error('导出Excel失败:', error)
    alert('导出Excel失败')
  }
}

const triggerImport = () => {
  fileInput.value.click()
}

const downloadTemplate = () => {
  const link = document.createElement('a')
  link.href = '/用户列表模板.xlsx'
  link.download = '用户列表模板.xlsx'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const handleImport = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  try {
    const data = await file.arrayBuffer()
    const workbook = XLSX.read(data, { type: 'array' })
    const sheetName = workbook.SheetNames[0]
    const worksheet = workbook.Sheets[sheetName]
    const jsonData = XLSX.utils.sheet_to_json(worksheet)

    if (!confirm(`准备导入 ${jsonData.length} 条用户数据，确认继续？`)) {
      event.target.value = ''
      return
    }

    const importData = jsonData.map(row => ({
      username: row['用户名'] || row['用户名'],
      email: row['邮箱'] || '',
      password: row['密码'] || '123456',
      role: row['角色'] === '管理员' ? 'admin' : 'user',
      status: row['状态'] === '正常' ? 1 : 0
    }))

    const result = await userApi.batchCreateUsers(importData)
    
    if (result.success) {
      alert(`导入完成！成功：${result.results.success} 条，失败：${result.results.failed} 条`)
      if (result.results.errors && result.results.errors.length > 0) {
        console.error('导入错误详情:', result.results.errors)
      }
      await fetchUsers()
    } else {
      alert(result.message || '导入失败')
    }
    
    event.target.value = ''
  } catch (error) {
    console.error('导入Excel失败:', error)
    alert('导入Excel失败，请检查文件格式')
    event.target.value = ''
  }
}


onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.users-wrapper {
  padding: 2rem;
  background-color: #f5f7fa;
  min-height: 100vh;
  width: calc(100% - 16rem);
  margin-left: 16rem;
}

.users-container {
  width: 100%;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.users-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.users-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1F2937;
  margin: 0;
}

.add-button {
  padding: 0.75rem 1.5rem;
  background-color: #3B82F6;
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

.add-button:hover {
  background-color: #2563EB;
}

.export-button {
  padding: 0.75rem 1.5rem;
  background-color: #10b981;
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

.export-button:hover:not(:disabled) {
  background-color: #059669;
}

.export-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.template-button {
  padding: 0.75rem 1.5rem;
  background-color: #6366f1;
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

.template-button:hover {
  background-color: #4f46e5;
}

.import-button {
  padding: 0.75rem 1.5rem;
  background-color: #f59e0b;
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

.import-button:hover {
  background-color: #d97706;
}

.search-bar {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.search-input-wrapper {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #9CA3AF;
  font-size: 1rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
  border: 1px solid #D1D5DB;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-button {
  padding: 0.75rem 1.5rem;
  background-color: #3B82F6;
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
}

.search-button:hover {
  background-color: #2563EB;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th {
  background-color: #F3F4F6;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
  border-bottom: 2px solid #E5E7EB;
}

.users-table td {
  padding: 1rem;
  border-bottom: 1px solid #E5E7EB;
  color: #4B5563;
  font-size: 0.875rem;
}

.users-table tr:hover td {
  background-color: #F9FAFB;
}

.role-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.role-badge.admin {
  background-color: #FEF3C7;
  color: #D97706;
}

.role-badge.user {
  background-color: #DBEAFE;
  color: #1E40AF;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.active {
  background-color: #D1FAE5;
  color: #065F46;
}

.status-badge.inactive {
  background-color: #FEE2E2;
  color: #DC2626;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.action-button {
  padding: 0.5rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-button.edit {
  background-color: #3B82F6;
  color: white;
}

.action-button.edit:hover {
  background-color: #2563EB;
}

.action-button.delete {
  background-color: #EF4444;
  color: white;
}

.action-button.delete:hover {
  background-color: #DC2626;
}

.no-data {
  text-align: center;
  padding: 3rem;
  color: #6B7280;
  font-size: 1rem;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0.5rem;
  margin-top: 2rem;
}

.pagination-button {
  padding: 0.5rem 0.75rem;
  background-color: white;
  border: 1px solid #D1D5DB;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #4B5563;
}

.pagination-button:hover:not(:disabled) {
  background-color: #F3F4F6;
  border-color: #9CA3AF;
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-number {
  padding: 0.5rem 0.75rem;
  border: 1px solid #D1D5DB;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #4B5563;
  min-width: 2rem;
  text-align: center;
}

.pagination-number:hover {
  background-color: #F3F4F6;
  border-color: #9CA3AF;
}

.pagination-number.active {
  background-color: #3B82F6;
  border-color: #3B82F6;
  color: white;
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
  border-radius: 1rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #E5E7EB;
}

.modal-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1F2937;
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6B7280;
  cursor: pointer;
  transition: color 0.2s ease;
}

.close-button:hover {
  color: #374151;
}

.modal-form {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.modal-form label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.modal-form input,
.modal-form select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #D1D5DB;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
}

.modal-form input:focus,
.modal-form select:focus {
  outline: none;
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.cancel-button {
  padding: 0.75rem 1.5rem;
  background-color: #F3F4F6;
  color: #374151;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.cancel-button:hover {
  background-color: #E5E7EB;
}

.submit-button {
  padding: 0.75rem 1.5rem;
  background-color: #3B82F6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.submit-button:hover:not(:disabled) {
  background-color: #2563EB;
}

.submit-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.mr-2 {
  margin-right: 0.5rem;
}
</style>
