<template>
  <el-container class="layout">
    <el-aside :width="sidebarW" class="app-aside aside">
      <div class="logo">
        <div class="logo-mark"><el-icon :size="20"><Monitor /></el-icon></div>
        <div class="logo-text">
          <span class="logo-name">社媒监测洞察</span>
          <span class="logo-sub">Digital Energy</span>
        </div>
      </div>

      <el-scrollbar class="menu-scroll">
        <el-menu :default-active="$route.path" router class="menu">
          <div class="menu-section">数据监测</div>
          <el-menu-item index="/"><el-icon><DataAnalysis /></el-icon><span>概览</span></el-menu-item>
          <el-menu-item index="/accounts"><el-icon><OfficeBuilding /></el-icon><span>公众号管理</span></el-menu-item>
          <el-menu-item index="/fetch"><el-icon><Download /></el-icon><span>内容抓取</span></el-menu-item>
          <el-menu-item index="/search"><el-icon><Search /></el-icon><span>关键词搜索</span></el-menu-item>
          <el-menu-item index="/articles"><el-icon><Document /></el-icon><span>文章库</span></el-menu-item>

          <div class="menu-section">智能洞察</div>
          <el-menu-item index="/analysis"><el-icon><MagicStick /></el-icon><span>智能分析</span></el-menu-item>
          <el-menu-item index="/scheduler"><el-icon><AlarmClock /></el-icon><span>定时任务</span></el-menu-item>
          <el-menu-item index="/reviews">
            <el-icon><Warning /></el-icon><span>待确认</span>
            <span v-if="pendingCount > 0" class="badge">{{ pendingCount > 99 ? '99+' : pendingCount }}</span>
          </el-menu-item>

          <div class="menu-section">系统</div>
          <el-sub-menu index="settings">
            <template #title><el-icon><Setting /></el-icon><span>系统设置</span></template>
            <el-menu-item index="/settings/llm">大模型配置</el-menu-item>
            <el-menu-item index="/settings/keys">数据源 Key</el-menu-item>
            <el-menu-item index="/settings/mcp">MCP 配置</el-menu-item>
            <el-menu-item index="/settings/services">检索服务</el-menu-item>
            <el-menu-item v-if="auth.isAdmin" index="/settings/users">用户管理</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-scrollbar>

      <div class="aside-foot">
        <span class="dot"></span>服务运行中 · v0.4.1
      </div>
    </el-aside>

    <el-container>
      <el-header class="app-header header">
        <div class="page-head">
          <div class="page-title">{{ $route.meta.title || '概览' }}</div>
          <div class="page-desc">{{ $route.meta.desc || todayStr }}</div>
        </div>
        <div class="header-right">
          <span class="internal-tag">内部系统</span>
          <el-tooltip v-if="pendingCount > 0" content="有待确认事项" placement="bottom">
            <el-badge :value="pendingCount" :max="99" class="bell-badge">
              <div class="icon-btn" @click="router.push('/reviews')"><el-icon :size="17"><Bell /></el-icon></div>
            </el-badge>
          </el-tooltip>
          <el-dropdown @command="onCommand" trigger="click">
            <div class="user-chip">
              <div class="avatar">{{ (auth.user?.username || '?')[0].toUpperCase() }}</div>
              <div class="user-meta">
                <span class="uname">{{ auth.user?.username }}</span>
                <span class="urole">{{ auth.isAdmin ? '管理员' : '成员' }}</span>
              </div>
              <el-icon class="caret"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="pwd"><el-icon><Key /></el-icon>修改密码</el-dropdown-item>
                <el-dropdown-item command="logout" divided><el-icon><SwitchButton /></el-icon>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="app-main main">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>

  <!-- 修改密码 -->
  <el-dialog v-model="pwdVisible" title="修改密码" width="420px">
    <el-form :model="pwdForm" label-width="90px">
      <el-form-item label="原密码"><el-input v-model="pwdForm.old_password" type="password" show-password /></el-form-item>
      <el-form-item label="新密码"><el-input v-model="pwdForm.new_password" type="password" show-password /></el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="pwdVisible = false">取消</el-button>
      <el-button type="primary" :loading="pwdLoading" @click="submitPwd">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../store/auth'
import { authApi, reviewApi } from '../api'

const auth = useAuthStore()
const router = useRouter()
const pendingCount = ref(0)
const pwdVisible = ref(false)
const pwdLoading = ref(false)
const pwdForm = reactive({ old_password: '', new_password: '' })
const sidebarW = '236px'
let timer = null

const todayStr = computed(() =>
  new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }))

async function loadPending() {
  try {
    const r = await reviewApi.pendingCount()
    pendingCount.value = r.pending
  } catch (e) { /* ignore */ }
}

function onCommand(cmd) {
  if (cmd === 'logout') {
    auth.logout()
    router.push('/login')
  } else if (cmd === 'pwd') {
    pwdForm.old_password = ''
    pwdForm.new_password = ''
    pwdVisible.value = true
  }
}

async function submitPwd() {
  if (!pwdForm.old_password || !pwdForm.new_password) {
    ElMessage.warning('请填写完整')
    return
  }
  pwdLoading.value = true
  try {
    await authApi.changePassword(pwdForm)
    ElMessage.success('密码已更新')
    pwdVisible.value = false
    auth.fetchMe()
  } finally {
    pwdLoading.value = false
  }
}

onMounted(() => {
  loadPending()
  timer = setInterval(loadPending, 30000)
})
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.layout { height: 100vh; }

/* ---- 侧边栏 ---- */
.aside { display: flex; flex-direction: column; }
.logo {
  display: flex; align-items: center; gap: 12px;
  padding: 18px 20px 16px;
}
.logo-mark {
  width: 38px; height: 38px; border-radius: 11px;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #e5323c 0%, #c7000b 100%);
  color: #fff;
  box-shadow: 0 4px 14px rgba(199, 0, 11, .45);
  flex-shrink: 0;
}
.logo-text { display: flex; flex-direction: column; }
.logo-name { color: #fff; font-size: 15.5px; font-weight: 700; letter-spacing: .02em; }
.logo-sub { color: #5d6578; font-size: 10.5px; letter-spacing: .14em; text-transform: uppercase; margin-top: 1px; }

.menu-scroll { flex: 1; }
.menu-section {
  padding: 16px 12px 6px;
  font-size: 11px; color: #525b6e; letter-spacing: .12em;
  user-select: none;
}
.menu { --el-menu-item-height: 44px; }
.badge {
  margin-left: auto;
  min-width: 20px; height: 18px; padding: 0 6px;
  border-radius: 9px;
  background: #f56c6c;
  color: #fff; font-size: 11px; font-weight: 600;
  display: inline-flex; align-items: center; justify-content: center;
}
.aside-foot {
  padding: 14px 20px;
  color: #525b6e; font-size: 12px;
  display: flex; align-items: center; gap: 7px;
  border-top: 1px solid rgba(255, 255, 255, .05);
}
.dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #2fa35c;
  box-shadow: 0 0 0 3px rgba(47, 163, 92, .18);
  animation: pulse 2.2s ease infinite;
}
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 3px rgba(47, 163, 92, .18); }
  50% { box-shadow: 0 0 0 5px rgba(47, 163, 92, .08); }
}

/* ---- 顶栏 ---- */
.header { display: flex; align-items: center; justify-content: space-between; padding: 0 24px; }
.page-head { display: flex; flex-direction: column; justify-content: center; }
.page-title { font-size: 17px; font-weight: 700; color: var(--ink-900); line-height: 1.3; }
.page-desc { font-size: 12px; color: var(--ink-400); margin-top: 1px; }

.header-right { display: flex; align-items: center; gap: 16px; }
.internal-tag {
  font-size: 12px; color: var(--ink-500);
  background: var(--ink-100);
  padding: 4px 10px; border-radius: 999px;
}
.icon-btn {
  width: 34px; height: 34px; border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  color: var(--ink-500); cursor: pointer;
  border: 1px solid var(--ink-200);
  background: #fff;
  transition: all .18s ease;
}
.icon-btn:hover { color: var(--brand-600); border-color: var(--brand-100); background: var(--brand-50); }
.bell-badge :deep(.el-badge__content) { border: none; }

.user-chip {
  display: flex; align-items: center; gap: 10px;
  padding: 5px 10px 5px 6px;
  border-radius: 999px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all .18s ease;
}
.user-chip:hover { background: var(--ink-100); border-color: var(--ink-200); }
.avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: linear-gradient(135deg, #e5323c, #a50009);
  color: #fff; font-size: 13px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.user-meta { display: flex; flex-direction: column; line-height: 1.2; }
.uname { font-size: 13px; font-weight: 600; color: var(--ink-900); }
.urole { font-size: 11px; color: var(--ink-400); }
.caret { font-size: 12px; color: var(--ink-400); }

/* ---- 主区 ---- */
.main { padding: 22px 24px; overflow-y: auto; }

/* 页面切换动画 */
.page-enter-active, .page-leave-active { transition: opacity .22s ease, transform .22s ease; }
.page-enter-from { opacity: 0; transform: translateY(10px); }
.page-leave-to { opacity: 0; transform: translateY(-6px); }
</style>
