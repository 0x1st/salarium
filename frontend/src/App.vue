<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from './store/user'
import { 
  User, 
  BarChart3, 
  Users, 
  Menu,
  X,
  Home,
  LogOut
} from 'lucide-vue-next'

const router = useRouter()
const user = useUserStore()
const sidebarCollapsed = ref(false)
const mobileMenuOpen = ref(false)

function handleLogout() {
  user.logout()
  router.push('/login')
}

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
  setTimeout(() => window.dispatchEvent(new Event('resize')), 0)
}

function toggleMobileMenu() {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

function closeMobileMenu() {
  mobileMenuOpen.value = false
}
</script>

<template>
  <!-- 登录页面单独布局 -->
  <div v-if="$route.path === '/login'" class="login-layout">
    <router-view />
  </div>

  <!-- 主应用布局 -->
  <div v-else class="app-layout">
    <!-- 桌面端侧边栏 -->
    <aside class="sidebar desktop-sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <div class="logo">
          <span v-if="!sidebarCollapsed" class="logo-text">Salarium</span>
        </div>
        <button class="collapse-btn" @click="toggleSidebar">
          <Home v-if="sidebarCollapsed" />
          <Menu v-else />
        </button>
      </div>
      
      <nav class="sidebar-nav">
        <router-link to="/stats" class="nav-item" @click="closeMobileMenu">
          <BarChart3 class="nav-icon" />
          <span v-if="!sidebarCollapsed" class="nav-text">统计分析</span>
        </router-link>
        <router-link to="/persons" class="nav-item" @click="closeMobileMenu">
          <Users class="nav-icon" />
          <span v-if="!sidebarCollapsed" class="nav-text">信息管理</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div v-if="user.token" class="user-profile">
          <div class="user-avatar">
            <User class="avatar-icon" />
          </div>
          <div v-if="!sidebarCollapsed" class="user-details">
            <div class="user-name">{{ user.username || '用户' }}</div>
            <button class="logout-link" @click="handleLogout">
              <LogOut class="logout-icon" />
              退出登录
            </button>
          </div>
          <button v-if="sidebarCollapsed" class="logout-btn-collapsed" @click="handleLogout" title="退出登录">
            <LogOut class="logout-icon" />
          </button>
        </div>
        <button v-else class="login-btn" @click="router.push('/login')">
          <User class="login-icon" />
          <span v-if="!sidebarCollapsed">登录</span>
        </button>
      </div>
    </aside>

    <!-- 移动端顶部导航 -->
    <header class="mobile-header">
      <div class="mobile-header-content">
        <button class="mobile-menu-btn" @click="toggleMobileMenu">
          <Menu v-if="!mobileMenuOpen" />
          <X v-else />
        </button>
        <div class="mobile-logo">
          <Home class="logo-icon" />
          <span class="logo-text">Salarium</span>
        </div>
        <div class="mobile-user">
          <el-dropdown v-if="user.token">
            <User class="user-icon" />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <button v-else class="mobile-login-btn" @click="router.push('/login')">
            <User />
          </button>
        </div>
      </div>
    </header>

    <!-- 移动端侧边栏 -->
    <aside class="sidebar mobile-sidebar" :class="{ open: mobileMenuOpen }">
      <nav class="sidebar-nav">
        <router-link to="/stats" class="nav-item" @click="closeMobileMenu">
          <BarChart3 class="nav-icon" />
          <span class="nav-text">统计分析</span>
        </router-link>
        <router-link to="/persons" class="nav-item" @click="closeMobileMenu">
          <Users class="nav-icon" />
          <span class="nav-text">信息管理</span>
        </router-link>
      </nav>
    </aside>

    <!-- 移动端遮罩 -->
    <div v-if="mobileMenuOpen" class="mobile-overlay" @click="closeMobileMenu"></div>

    <!-- 主内容区域 -->
    <main class="main-content" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <div class="content-wrapper">
        <router-view />
      </div>
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f8fafc;
}

.login-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 桌面端侧边栏 */
.desktop-sidebar {
  width: 280px;
  background: #ffffff;
  border-right: 1px solid #e2e8f0;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
  transition: width 0.3s ease;
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.desktop-sidebar.collapsed {
  width: 80px;
}

.sidebar-header {
  padding: 1.5rem 1rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  z-index: 2;
}

.desktop-sidebar.collapsed .sidebar-header {
  justify-content: center;
  padding: 1.5rem 0.5rem;
}

.desktop-sidebar.collapsed .logo {
  display: none;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  width: 32px;
  height: 32px;
  color: #3b82f6;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

.collapse-btn {
  background: none;
  border: none;
  padding: 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  color: #64748b;
  transition: all 0.2s;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.collapse-btn:hover {
  background-color: #f1f5f9;
  color: #3b82f6;
}

.collapse-btn svg {
  width: 24px;
  height: 24px;
  display: block;
}

.desktop-sidebar.collapsed .collapse-btn svg {
  width: 28px;
  height: 28px;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  margin: 0.25rem 1rem;
  border-radius: 0.5rem;
  color: #64748b;
  text-decoration: none;
  transition: all 0.2s;
  font-weight: 500;
}

.nav-item:hover {
  background-color: #f1f5f9;
  color: #3b82f6;
}

.nav-item.router-link-active {
  background-color: #dbeafe;
  color: #3b82f6;
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #e2e8f0;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.user-profile:hover {
  background: linear-gradient(135deg, #f1f5f9 0%, #ddd6fe 100%);
  border-color: #3b82f6;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.user-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.avatar-icon {
  width: 18px;
  height: 18px;
  color: white;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logout-link {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: #64748b;
  font-size: 12px;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s ease;
}

.logout-link:hover {
  color: #ef4444;
}

.logout-link .logout-icon {
  width: 12px;
  height: 12px;
}

.logout-btn-collapsed {
  background: none;
  border: none;
  padding: 8px;
  border-radius: 50%;
  cursor: pointer;
  color: #64748b;
  transition: all 0.2s ease;
}

.logout-btn-collapsed:hover {
  background-color: #fee2e2;
  color: #ef4444;
}

.logout-btn-collapsed .logout-icon {
  width: 16px;
  height: 16px;
}
.language-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background: none;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.language-btn:hover {
  background-color: #f1f5f9;
  border-color: #10b981;
  color: #10b981;
}

.language-icon {
  width: 20px;
  height: 20px;
}

.logout-btn, .login-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: none;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.logout-btn:hover, .login-btn:hover {
  background-color: #f1f5f9;
  border-color: #3b82f6;
  color: #3b82f6;
}

.logout-icon, .login-icon {
  width: 20px;
  height: 20px;
}

/* 移动端样式 */
.mobile-header {
  display: none;
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1001;
}

.mobile-header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
}

.mobile-menu-btn {
  background: none;
  border: none;
  padding: 0.5rem;
  cursor: pointer;
  color: #64748b;
}

.mobile-logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.mobile-user {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.mobile-user .user-icon {
  width: 24px;
  height: 24px;
  color: #64748b;
}

.mobile-language-btn {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.mobile-language-btn:hover {
  background-color: #f1f5f9;
  color: #10b981;
}

.mobile-login-btn {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.mobile-login-btn:hover {
  background-color: #f1f5f9;
  color: #3b82f6;
}

.mobile-sidebar {
  display: none;
  position: fixed;
  top: 0;
  left: -280px;
  width: 280px;
  height: 100vh;
  background: #ffffff;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  transition: left 0.3s ease;
  z-index: 1002;
  padding-top: 80px;
}

.mobile-sidebar.open {
  left: 0;
}

.mobile-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1001;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  margin-left: 280px;
  transition: margin-left 0.3s ease;
  position: relative;
  z-index: 1;
  min-height: 100vh;
}

.main-content.sidebar-collapsed {
  margin-left: 80px;
}

.content-wrapper {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .desktop-sidebar {
    display: none;
  }
  
  .mobile-header {
    display: block;
  }
  
  .mobile-sidebar {
    display: block;
  }
  
  .mobile-overlay {
    display: block;
  }
  
  .main-content {
    margin-left: 0;
    padding-top: 80px;
  }
  
  .content-wrapper {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .content-wrapper {
    padding: 0.5rem;
  }
}
</style>
