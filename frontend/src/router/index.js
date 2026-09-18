import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('../layout/MainLayout.vue'),
    children: [
      { path: '', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '概览', desc: '全网舆情数据总览与重点动态' } },
      { path: 'accounts', name: 'Accounts', component: () => import('../views/Accounts.vue'), meta: { title: '公众号管理', desc: '维护监测对象、分组与标签' } },
      { path: 'fetch', name: 'Fetch', component: () => import('../views/Fetch.vue'), meta: { title: '内容抓取', desc: '发起抓取任务，实时跟踪进度' } },
      { path: 'search', name: 'Search', component: () => import('../views/Search.vue'), meta: { title: '关键词搜索', desc: '微信搜一搜检索文章，选中后批量下载 / 分析' } },
      { path: 'articles', name: 'Articles', component: () => import('../views/Articles.vue'), meta: { title: '文章库', desc: '检索、筛选与导出已抓取文章' } },
      { path: 'articles/:id', name: 'ArticleDetail', component: () => import('../views/ArticleDetail.vue'), meta: { title: '文章详情', desc: '正文、指标趋势、评论与分析记录' } },
      { path: 'analysis', name: 'Analysis', component: () => import('../views/Analysis.vue'), meta: { title: '智能分析', desc: '基于大模型的多维度内容洞察' } },
      { path: 'scheduler', name: 'Scheduler', component: () => import('../views/Scheduler.vue'), meta: { title: '定时任务', desc: '自动化抓取计划与排名报告' } },
      { path: 'reviews', name: 'Reviews', component: () => import('../views/Reviews.vue'), meta: { title: '待确认', desc: '文章删除与评论异常的人工复核队列' } },
      // 设置
      { path: 'settings/llm', name: 'LlmConfig', component: () => import('../views/settings/LlmConfig.vue'), meta: { title: '大模型配置', desc: 'OpenAI 兼容协议模型接入' } },
      { path: 'settings/keys', name: 'Keys', component: () => import('../views/settings/Keys.vue'), meta: { title: '数据源 Key', desc: 'dajiala API Key 池与配额管理' } },
      { path: 'settings/mcp', name: 'Mcp', component: () => import('../views/settings/Mcp.vue'), meta: { title: 'MCP 配置', desc: 'MCP 服务器接入管理' } },
      { path: 'settings/services', name: 'Services', component: () => import('../views/settings/Services.vue'), meta: { title: '检索服务', desc: '云端浏览器与检索服务配置' } },
      { path: 'settings/users', name: 'Users', component: () => import('../views/settings/Users.vue'), meta: { title: '用户管理', desc: '账号、角色与权限', admin: true } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.public) return true
  if (!auth.isLoggedIn) return { path: '/login' }
  if (to.meta.admin && !auth.isAdmin) return { path: '/' }
  return true
})

export default router
