import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'
import { useAuthStore } from '../store/auth'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 60000,
})

// 请求拦截：附带 token
request.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

// 响应拦截：统一错误提示，401 跳登录
request.interceptors.response.use(
  (resp) => resp.data,
  async (error) => {
    const resp = error.response
    let msg = resp?.data?.detail || error.message || '请求失败'
    // 下载类接口（blob）的错误响应也是 Blob，需解析出 JSON 里的 detail
    if (resp?.data instanceof Blob) {
      try { msg = JSON.parse(await resp.data.text()).detail || msg } catch { /* 保持原 msg */ }
    }
    if (resp?.status === 401) {
      const auth = useAuthStore()
      auth.logout()
      if (router.currentRoute.value.path !== '/login') {
        ElMessage.error('登录已过期，请重新登录')
        router.push('/login')
      }
    } else {
      ElMessage.error(typeof msg === 'string' ? msg : JSON.stringify(msg))
    }
    return Promise.reject(error)
  },
)

export default request
