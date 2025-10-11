<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { ElMessage } from 'element-plus'
import { User, Lock } from 'lucide-vue-next'

// Form data
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const isRegisterMode = ref(false)

// Router and store
const router = useRouter()
const user = useUserStore()

/**
 * Toggle between login and register modes
 */
function toggleMode() {
  isRegisterMode.value = !isRegisterMode.value
  // Clear form when switching modes
  username.value = ''
  password.value = ''
  confirmPassword.value = ''
}

/**
 * Validate form inputs
 */
function validateForm() {
  if (!username.value.trim()) {
    ElMessage.warning('请输入用户名')
    return false
  }
  
  if (!password.value) {
    ElMessage.warning('请输入密码')
    return false
  }
  
  if (isRegisterMode.value && password.value !== confirmPassword.value) {
    ElMessage.warning('密码不匹配')
    return false
  }
  
  return true
}

/**
 * Handle login submission
 */
async function handleLogin() {
  try {
    const { data } = await axios.post('/api/auth/login', {
      username: username.value,
      password: password.value
    })
    
    user.setToken(data.access_token)
    user.setUsername(username.value)
    ElMessage.success('登录成功')
    router.push('/stats')
  } catch (error) {
    console.error('Login error:', error)
    ElMessage.error('登录失败，请检查用户名和密码')
  }
}

/**
 * Handle registration submission
 */
async function handleRegister() {
  try {
    await axios.post('/api/auth/register', {
      username: username.value,
      password: password.value
    })
    
    ElMessage.success('注册成功')
    
    // Auto login after successful registration
    await handleLogin()
  } catch (error) {
    console.error('Registration error:', error)
    ElMessage.error('注册失败')
  }
}

/**
 * Handle form submission
 */
async function onSubmit() {
  if (!validateForm()) return
  
  loading.value = true
  
  try {
    if (isRegisterMode.value) {
      await handleRegister()
    } else {
      await handleLogin()
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <!-- Animated Background -->
    <div class="background-animation">
      <div class="floating-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
        <div class="shape shape-5"></div>
      </div>
    </div>

    <!-- Login/Register Card -->
    <div class="login-card">
      <!-- Logo and Title -->
      <div class="header-section">
        <div class="logo-container">
          <div class="logo-icon">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
            </svg>
          </div>
          <div class="logo-glow"></div>
        </div>
        <h1 class="main-title">
          {{ isRegisterMode ? '创建账户' : 'Salarium' }}
        </h1>
        <p class="tagline">简单 · 高效</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="onSubmit" class="form-container">
        <!-- Username Field -->
        <div class="input-group">
          <label class="input-label">
            <User class="input-icon" />
            用户名
          </label>
          <div class="input-wrapper">
            <input
              v-model="username"
              type="text"
              class="form-input"
              placeholder="请输入用户名"
              :disabled="loading"
              required
            />
            <div class="input-border"></div>
          </div>
        </div>

        <!-- Password Field -->
        <div class="input-group">
          <label class="input-label">
            <Lock class="input-icon" />
            密码
          </label>
          <div class="input-wrapper">
            <input
              v-model="password"
              type="password"
              class="form-input"
              placeholder="请输入密码"
              :disabled="loading"
              required
            />
            <div class="input-border"></div>
          </div>
        </div>

        <!-- Confirm Password Field (Register Mode Only) -->
        <div v-if="isRegisterMode" class="input-group">
          <label class="input-label">
            <Lock class="input-icon" />
            确认密码
          </label>
          <div class="input-wrapper">
            <input
              v-model="confirmPassword"
              type="password"
              class="form-input"
              placeholder="请再次输入密码"
              :disabled="loading"
              required
            />
            <div class="input-border"></div>
          </div>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          class="submit-btn"
          :disabled="loading"
        >
          <span v-if="loading" class="loading-spinner"></span>
          <span v-else>{{ isRegisterMode ? '注册' : '登录' }}</span>
        </button>

        <!-- Mode Toggle -->
        <div class="mode-toggle">
          <p class="toggle-text">
            {{ isRegisterMode ? '已有账户？' : '还没有账户？' }}
            <button
              type="button"
              @click="toggleMode"
              class="toggle-link"
              :disabled="loading"
            >
              {{ isRegisterMode ? '登录' : '注册' }}
            </button>
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
/* Main Container */
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  position: relative;
  overflow: hidden;
}

/* Animated Background */
.background-animation {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.floating-shapes {
  position: relative;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 80px;
  height: 80px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 120px;
  height: 120px;
  top: 20%;
  right: 10%;
  animation-delay: 1s;
}

.shape-3 {
  width: 60px;
  height: 60px;
  bottom: 30%;
  left: 20%;
  animation-delay: 2s;
}

.shape-4 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  right: 20%;
  animation-delay: 3s;
}

.shape-5 {
  width: 40px;
  height: 40px;
  top: 50%;
  left: 50%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
    opacity: 0.7;
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
    opacity: 1;
  }
}

/* Language Toggle */
.language-toggle {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 10;
}

.language-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: white;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: pointer;
}

.language-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

/* Login Card */
.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  padding: 2.5rem;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
  animation: slideUp 0.8s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Header Section */
.header-section {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-container {
  position: relative;
  display: inline-block;
  margin-bottom: 1.5rem;
}

.logo-icon {
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 2;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
}

.logo-glow {
  position: absolute;
  top: -5px;
  left: -5px;
  right: -5px;
  bottom: -5px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  opacity: 0.3;
  animation: pulse 2s ease-in-out infinite;
  z-index: 1;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.5;
  }
}

.main-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  color: #4a5568;
  font-size: 1.1rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.tagline {
  color: #718096;
  font-size: 0.875rem;
}

/* Form Container */
.form-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Input Groups */
.input-group {
  position: relative;
}

.input-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 0.5rem;
}

.input-icon {
  width: 1rem;
  height: 1rem;
  color: #667eea;
}

.input-wrapper {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 1rem 1.25rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  outline: none;
}

.form-input:focus {
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.95);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
}

.form-input:focus + .input-border {
  transform: scaleX(1);
}

.input-border {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transform: scaleX(0);
  transition: transform 0.3s ease;
  border-radius: 1px;
}

/* Submit Button */
.submit-btn {
  position: relative;
  width: 100%;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  margin-top: 0.5rem;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-content {
  position: relative;
  z-index: 2;
}

.btn-glow {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.submit-btn:hover .btn-glow {
  left: 100%;
}

.loading-text {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.loading-text::after {
  content: '';
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Mode Toggle */
.mode-toggle {
  margin-top: 1.5rem;
  text-align: center;
}

.toggle-text {
  font-size: 0.875rem;
  color: #718096;
}

.toggle-btn {
  color: #667eea;
  font-weight: 600;
  margin-left: 0.25rem;
  background: none;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: underline;
  text-decoration-color: transparent;
}

.toggle-btn:hover:not(:disabled) {
  color: #764ba2;
  text-decoration-color: #764ba2;
}

.toggle-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Responsive Design */
@media (max-width: 480px) {
  .login-card {
    margin: 1rem;
    padding: 2rem 1.5rem;
  }
  
  .main-title {
    font-size: 1.5rem;
  }
  
  .language-toggle {
    top: 0.5rem;
    right: 0.5rem;
  }
  
  .language-btn {
    padding: 0.5rem 0.75rem;
    font-size: 0.875rem;
  }
}

/* Animation for smooth transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>