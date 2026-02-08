import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store/user'

const Login = () => import('../views/Login.vue')
const Persons = () => import('../views/Persons.vue')
const Salaries = () => import('../views/Salaries.vue')
const SalaryFields = () => import('../views/SalaryFields.vue')

// Stats module with tabs/routes
const StatsIndex = () => import('../views/stats/Index.vue')
const StatsNet = () => import('../views/stats/Net.vue')
const StatsComposition = () => import('../views/stats/Composition.vue')
const StatsDeductions = () => import('../views/stats/Deductions.vue')
const StatsTable = () => import('../views/stats/Table.vue')

const routes = [
  { path: '/', redirect: '/stats' },
  { path: '/login', component: Login },
  {
    path: '/stats',
    component: StatsIndex,
    redirect: { name: 'stats-net' },
    meta: { title: '统计分析' },
    children: [
      { path: 'net', name: 'stats-net', component: StatsNet, meta: { title: '概览' } },
      { path: 'composition', name: 'stats-composition', component: StatsComposition, meta: { title: '收入构成' } },
      { path: 'deductions', name: 'stats-deductions', component: StatsDeductions, meta: { title: '扣除分析' } },
      { path: 'table', name: 'stats-table', component: StatsTable, meta: { title: '明细表' } },
    ],
  },
  { path: '/persons', component: Persons },
  { path: '/salaries/:personId?', component: Salaries },
  { path: '/salary-fields', component: SalaryFields, meta: { title: '自定义字段' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const user = useUserStore()
  const publicPaths = ['/login']
  
  if (!user.token && !publicPaths.includes(to.path)) {
    return {
      path: '/login',
      query: { redirect: to.fullPath }
    }
  }
})

export default router
