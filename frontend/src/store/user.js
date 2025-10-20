import { defineStore } from 'pinia'
import { useStatsStore } from './stats'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    username: '',
  }),
  actions: {
    setToken(t) {
      this.token = t
      localStorage.setItem('token', t)
      // Reset all cached business data when switching/starting a session
      try {
        const stats = useStatsStore()
        stats.resetAll()
      } catch (e) {
        // ignore if store not initialized yet
      }
    },
    logout() {
      this.token = ''
      this.username = ''
      localStorage.removeItem('token')
      // Thoroughly clear business caches
      try {
        const stats = useStatsStore()
        stats.resetAll()
      } catch (e) {
        // ignore if store not initialized yet
      }
    },
    setUsername(name) {
      this.username = name
    },
  },
})