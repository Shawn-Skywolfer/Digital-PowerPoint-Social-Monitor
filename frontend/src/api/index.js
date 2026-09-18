import request from './request'

// 认证
export const authApi = {
  login: (data) => request.post('/auth/login', data),
  me: () => request.get('/auth/me'),
  changePassword: (data) => request.post('/auth/change-password', data),
}

// 用户
export const userApi = {
  list: () => request.get('/users'),
  create: (data) => request.post('/users', data),
  update: (id, data) => request.patch(`/users/${id}`, data),
  remove: (id) => request.delete(`/users/${id}`),
}

// 公众号
export const accountApi = {
  list: () => request.get('/accounts'),
  search: (data) => request.post('/accounts/search', data),
  add: (data) => request.post('/accounts/add', data),
  importAccounts: (data) => request.post('/accounts/import', data),
  update: (id, data) => request.patch(`/accounts/${id}`, data),
  remove: (id) => request.delete(`/accounts/${id}`),
  // 分组
  groups: () => request.get('/accounts/groups'),
  createGroup: (data) => request.post('/accounts/groups', data),
  renameGroup: (id, data) => request.patch(`/accounts/groups/${id}`, data),
  removeGroup: (id) => request.delete(`/accounts/groups/${id}`),
  assignGroup: (data) => request.post('/accounts/groups/assign', data),
}

// 抓取
export const fetchApi = {
  fields: () => request.get('/fetch/fields'),
  profiles: () => request.get('/fetch/profiles'),
  createProfile: (data) => request.post('/fetch/profiles', data),
  removeProfile: (id) => request.delete(`/fetch/profiles/${id}`),
  createTask: (data, config) => request.post('/fetch/tasks', data, config),
  tasks: (limit = 50) => request.get('/fetch/tasks', { params: { limit } }),
  task: (id) => request.get(`/fetch/tasks/${id}`),
  taskArticles: (id) => request.get(`/fetch/tasks/${id}/articles`),
  cancel: (id) => request.post(`/fetch/tasks/${id}/cancel`),
  removeTask: (id) => request.delete(`/fetch/tasks/${id}`),
}

// 关键词搜索（搜一搜）
export const searchApi = {
  articles: (data, config) => request.post('/search/articles', data, config),
  import: (items, config) => request.post('/search/import', { items }, config),
}

// 文章
export const articleApi = {
  list: (params) => request.get('/articles', { params }),
  detail: (id) => request.get(`/articles/${id}`),
  comments: (id) => request.get(`/articles/${id}/comments`),
  metrics: (id) => request.get(`/articles/${id}/metrics`),
}

// 导出（返回 blob）
export const exportApi = {
  articles: (params) => request.get('/export/articles', { params, responseType: 'blob' }),
  comments: (params) => request.get('/export/comments', { params, responseType: 'blob' }),
  analysis: (params) => request.get('/export/analysis', { params, responseType: 'blob' }),
  collection: (id, params) => request.get(`/export/collection/${id}`, { params, responseType: 'blob' }),
}

// 分析
export const analysisApi = {
  modules: () => request.get('/analysis/modules'),
  createModule: (data) => request.post('/analysis/modules', data),
  updateModule: (id, data) => request.patch(`/analysis/modules/${id}`, data),
  removeModule: (id) => request.delete(`/analysis/modules/${id}`),
  addDimension: (moduleId, data) => request.post(`/analysis/modules/${moduleId}/dimensions`, data),
  updateDimension: (id, data) => request.patch(`/analysis/dimensions/${id}`, data),
  removeDimension: (id) => request.delete(`/analysis/dimensions/${id}`),
  exportModule: (id) => request.get(`/analysis/modules/${id}/export`, { responseType: 'blob' }),
  importModule: (data) => request.post('/analysis/modules/import', data),
  run: (data, config) => request.post('/analysis/run', data, config),
  results: (params) => request.get('/analysis/results', { params }),
  // 聚合分析报告
  collections: (limit = 50) => request.get('/analysis/collections', { params: { limit } }),
  collection: (id) => request.get(`/analysis/collections/${id}`),
  removeCollection: (id) => request.delete(`/analysis/collections/${id}`),
}

// LLM 配置
export const llmApi = {
  list: () => request.get('/llm/configs'),
  create: (data) => request.post('/llm/configs', data),
  update: (id, data) => request.patch(`/llm/configs/${id}`, data),
  remove: (id) => request.delete(`/llm/configs/${id}`),
  test: (id) => request.post(`/llm/configs/${id}/test`),
}

// dajiala Key
export const keyApi = {
  list: () => request.get('/keys'),
  create: (data) => request.post('/keys', data),
  update: (id, data) => request.patch(`/keys/${id}`, data),
  remove: (id) => request.delete(`/keys/${id}`),
  check: (id) => request.post(`/keys/${id}/check`),
}

// MCP
export const mcpApi = {
  available: () => request.get('/mcp/available'),
  list: () => request.get('/mcp/servers'),
  create: (data) => request.post('/mcp/servers', data),
  update: (id, data) => request.patch(`/mcp/servers/${id}`, data),
  remove: (id) => request.delete(`/mcp/servers/${id}`),
  test: (id) => request.post(`/mcp/servers/${id}/test`),
}

// LightPanda / Tavily 服务
export const serviceApi = {
  list: () => request.get('/services'),
  create: (data) => request.post('/services', data),
  update: (id, data) => request.patch(`/services/${id}`, data),
  remove: (id) => request.delete(`/services/${id}`),
  test: (id) => request.post(`/services/${id}/test`),
}

// 定时任务 & 排名
export const schedulerApi = {
  jobs: () => request.get('/scheduler/jobs'),
  create: (data) => request.post('/scheduler/jobs', data),
  update: (id, data) => request.patch(`/scheduler/jobs/${id}`, data),
  remove: (id) => request.delete(`/scheduler/jobs/${id}`),
  run: (id) => request.post(`/scheduler/jobs/${id}/run`),
  reports: (params) => request.get('/scheduler/reports', { params }),
  ranking: (params) => request.get('/scheduler/ranking', { params }),
}

// 待确认
export const reviewApi = {
  list: (status) => request.get('/reviews', { params: status ? { status_filter: status } : {} }),
  pendingCount: () => request.get('/reviews/pending-count'),
  resolve: (id, data) => request.post(`/reviews/${id}/resolve`, data),
}

// Dashboard
export const dashboardApi = {
  stats: () => request.get('/dashboard/stats'),
  topArticles: (params) => request.get('/dashboard/top-articles', { params }),
}
