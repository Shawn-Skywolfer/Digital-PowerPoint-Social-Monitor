import { defineStore } from 'pinia'
import { authApi } from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  }),
  getters: {
    isLoggedIn: (s) => !!s.token,
    isAdmin: (s) => s.user?.role === 'admin',
    mustChangePassword: (s) => !!s.user?.must_change_password,
  },
  actions: {
    async login(username, password) {
      const resp = await authApi.login({ username, password })
      this.token = resp.access_token
      this.user = resp.user
      localStorage.setItem('token', this.token)
      localStorage.setItem('user', JSON.stringify(resp.user))
      return resp
    },
    async fetchMe() {
      const me = await authApi.me()
      this.user = me
      localStorage.setItem('user', JSON.stringify(me))
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
  },
})
