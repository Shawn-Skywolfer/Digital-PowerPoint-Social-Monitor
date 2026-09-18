<template>
  <div class="login-wrap">
    <!-- 品牌展示面板 -->
    <div class="brand-panel">
      <div class="brand-inner">
        <div class="brand-logo">
          <div class="brand-mark"><el-icon :size="26"><Monitor /></el-icon></div>
          <span>社媒监测洞察系统</span>
        </div>
        <h2 class="brand-slogan">让舆情洞察<br />更快一步</h2>
        <p class="brand-desc">公众号内容自动抓取 · 指标追踪 · 大模型智能分析，为华为数字能源营销团队提供一站式社媒情报支持。</p>
        <ul class="feature-list">
          <li><el-icon><CircleCheckFilled /></el-icon>多账号批量监测，数据自动归集</li>
          <li><el-icon><CircleCheckFilled /></el-icon>阅读 / 点赞 / 评论全指标趋势追踪</li>
          <li><el-icon><CircleCheckFilled /></el-icon>大模型多维度分析与聚合报告</li>
        </ul>
      </div>
      <div class="brand-foot">华为数字能源 Marketing · 仅限内部使用</div>
      <div class="glow glow-1"></div>
      <div class="glow glow-2"></div>
    </div>

    <!-- 登录表单 -->
    <div class="form-panel">
      <div class="login-box">
        <h1>欢迎回来</h1>
        <p class="login-sub">请使用内部账号登录系统</p>
        <el-form :model="form" @submit.prevent="onLogin">
          <el-form-item>
            <el-input v-model="form.username" size="large" placeholder="用户名" :prefix-icon="User" />
          </el-form-item>
          <el-form-item>
            <el-input v-model="form.password" type="password" size="large" placeholder="密码"
              :prefix-icon="Lock" show-password @keyup.enter="onLogin" />
          </el-form-item>
          <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="onLogin">
            登 录
          </el-button>
        </el-form>
        <p class="login-foot">首次登录请使用管理员分配的初始密码，登录后需修改</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const router = useRouter()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

async function onLogin() {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const resp = await auth.login(form.username, form.password)
    ElMessage.success('登录成功')
    if (resp.must_change_password) {
      ElMessage.warning('首次登录，请尽快修改默认密码')
    }
    router.push('/')
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrap { height: 100vh; display: flex; overflow: hidden; }

/* ---- 左：品牌面板 ---- */
.brand-panel {
  flex: 1.15;
  position: relative;
  background: linear-gradient(160deg, #131b2c 0%, #0c1220 55%, #1a0d14 100%);
  display: flex; flex-direction: column; justify-content: space-between;
  padding: 56px 64px;
  overflow: hidden;
}
.glow {
  position: absolute; border-radius: 50%;
  filter: blur(90px); pointer-events: none;
}
.glow-1 { width: 420px; height: 420px; background: rgba(199, 0, 11, .28); top: -120px; right: -100px; }
.glow-2 { width: 360px; height: 360px; background: rgba(64, 96, 199, .18); bottom: -140px; left: -80px; }

.brand-inner { position: relative; z-index: 1; max-width: 520px; }
.brand-logo { display: flex; align-items: center; gap: 12px; color: #fff; font-size: 17px; font-weight: 600; }
.brand-mark {
  width: 42px; height: 42px; border-radius: 12px;
  background: linear-gradient(135deg, #e5323c, #a50009);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 6px 20px rgba(199, 0, 11, .5);
}
.brand-slogan {
  color: #fff; font-size: 42px; font-weight: 700; line-height: 1.25;
  margin: 64px 0 18px; letter-spacing: .01em;
}
.brand-desc { color: #8a93a8; font-size: 15px; line-height: 1.9; margin: 0 0 36px; }
.feature-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 14px; }
.feature-list li { color: #b7bfce; font-size: 14px; display: flex; align-items: center; gap: 10px; }
.feature-list .el-icon { color: #e5323c; font-size: 16px; }
.brand-foot { position: relative; z-index: 1; color: #525b6e; font-size: 12.5px; }

/* ---- 右：表单面板 ---- */
.form-panel {
  width: 460px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  background: #fff;
}
.login-box { width: 340px; }
.login-box h1 { font-size: 26px; font-weight: 700; margin: 0 0 6px; color: var(--ink-900); }
.login-sub { color: var(--ink-400); font-size: 13.5px; margin: 0 0 30px; }
.login-btn { width: 100%; margin-top: 8px; height: 44px; font-size: 15px; letter-spacing: .3em; }
.login-foot { margin-top: 26px; color: var(--ink-300); font-size: 12px; text-align: center; }

@media (max-width: 900px) {
  .brand-panel { display: none; }
  .form-panel { width: 100%; }
}
</style>
