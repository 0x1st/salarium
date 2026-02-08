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
          <Home class="logo-icon" />
          <span v-if="!sidebarCollapsed" class="logo-text">Salarium</span>
        </div>
        <button class="collapse-btn" @click="toggleSidebar">
          <Menu />
        </button>
      </div>
      
      <nav class="sidebar-nav">
        <router-link to="/stats/net" class="nav-item" @click="closeMobileMenu">
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
        <router-link to="/stats/net" class="nav-item" @click="closeMobileMenu">
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
        <router-view v-slot="{ Component, route }">
          <transition name="page" mode="out-in">
            <div class="page-shell" :key="route.path">
              <component :is="Component" />
            </div>
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background-color: #fdfcfb;
}

.login-layout {
  min-height: 100vh;
  background: #fdfcfb;
}

/* 桌面端侧边栏 */
.desktop-sidebar {
  width: 280px;
  background: #ffffff;
  border-right: 1px solid #e5e0dc;
  box-shadow: none;
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
  padding: 1.75rem 1.25rem;
  border-bottom: 1px solid #e5e0dc;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  z-index: 2;
}

.desktop-sidebar.collapsed .sidebar-header {
  justify-content: center;
  padding: 1.75rem 0.5rem;
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
  width: 28px;
  height: 28px;
  color: #da7756;
}

.logo-text {
  font-family: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
  font-size: 1.375rem;
  font-weight: 500;
  color: #2d2a26;
  letter-spacing: -0.01em;
}

.collapse-btn {
  background: none;
  border: none;
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  color: #6b6560;
  transition: all 0.2s;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.collapse-btn:hover {
  background-color: #f5e6e0;
  color: #da7756;
}

.collapse-btn svg {
  width: 22px;
  height: 22px;
  display: block;
}

.desktop-sidebar.collapsed .collapse-btn svg {
  width: 26px;
  height: 26px;
}

.sidebar-nav {
  flex: 1;
  padding: 1.25rem 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.25rem;
  margin: 0.25rem 1rem;
  border-radius: 8px;
  color: #6b6560;
  text-decoration: none;
  transition: all 0.2s;
  font-weight: 450;
}

.nav-item:hover {
  background-color: #f5e6e0;
  color: #da7756;
}

.nav-item.router-link-active {
  background-color: #f5e6e0;
  color: #da7756;
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.sidebar-footer {
  padding: 1.25rem;
  border-top: 1px solid #e5e0dc;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem;
  margin-bottom: 0.5rem;
  background: #faf5f3;
  border-radius: 10px;
  border: 1px solid #e5e0dc;
  transition: all 0.2s ease;
}

.user-profile:hover {
  background: #f5e6e0;
  border-color: #da7756;
}

.user-avatar {
  width: 36px;
  height: 36px;
  background: #da7756;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
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
  font-weight: 500;
  color: #2d2a26;
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
  color: #6b6560;
  font-size: 12px;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s ease;
}

.logout-link:hover {
  color: #c45c5c;
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
  color: #6b6560;
  transition: all 0.2s ease;
}

.logout-btn-collapsed:hover {
  background-color: #f5e6e0;
  color: #c45c5c;
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
  border: 1px solid #e5e0dc;
  border-radius: 8px;
  color: #6b6560;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 450;
}

.language-btn:hover {
  background-color: #f5f3f1;
  border-color: #5a8a6e;
  color: #5a8a6e;
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
  border: 1px solid #e5e0dc;
  border-radius: 8px;
  color: #6b6560;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 450;
}

.logout-btn:hover, .login-btn:hover {
  background-color: #f5e6e0;
  border-color: #da7756;
  color: #da7756;
}

.logout-icon, .login-icon {
  width: 20px;
  height: 20px;
}

/* 移动端样式 */
.mobile-header {
  display: none;
  background: #ffffff;
  border-bottom: 1px solid #e5e0dc;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
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
  color: #6b6560;
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
  color: #6b6560;
}

.mobile-language-btn {
  background: none;
  border: none;
  color: #6b6560;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.2s;
}

.mobile-language-btn:hover {
  background-color: #f5f3f1;
  color: #5a8a6e;
}

.mobile-login-btn {
  background: none;
  border: none;
  color: #6b6560;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.2s;
}

.mobile-login-btn:hover {
  background-color: #f5e6e0;
  color: #da7756;
}

.mobile-sidebar {
  display: none;
  position: fixed;
  top: 0;
  left: -280px;
  width: 280px;
  height: 100vh;
  background: #ffffff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.08);
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
  background: rgba(0, 0, 0, 0.4);
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

.page-shell {
  min-height: 100%;
}

.content-wrapper {
  padding: 0;
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
}

/* Page transition animations */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(-6px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

.page-enter-to,
.page-leave-from {
  opacity: 1;
  transform: translateY(0);
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
    padding: 0;
  }
}
</style>
