import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createPinia } from 'pinia'
// Element Plus visual alignment overrides (align tables with Salaries page)
import './assets/element-plus-overrides.css'
// Shared styles for consistent UI
import './styles/shared.css'
import { setupAxiosInterceptors } from './utils/axios'
import { useUserStore } from './store/user'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElementPlus)

const userStore = useUserStore()
setupAxiosInterceptors(router, userStore)

app.mount('#app')
