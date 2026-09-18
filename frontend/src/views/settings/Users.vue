<template>
  <el-card shadow="never" class="panel">
    <template #header>
      <div class="card-headbar"><div class="panel-title"><span class="bar"></span>用户管理<span class="text-sub">仅管理员可见</span></div>
        <el-button type="primary" @click="open()">新增用户</el-button></div>
    </template>
    <el-table :data="rows" v-loading="loading">
      <el-table-column prop="username" label="用户名" min-width="140" />
      <el-table-column label="角色" width="120">
        <template #default="{ row }">
          <el-tag size="small" :type="row.role === 'admin' ? 'danger' : 'primary'" effect="plain">
            {{ row.role === 'admin' ? '管理员' : '成员' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="110" align="center">
        <template #default="{ row }">
          <el-tag size="small" :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          <div v-if="row.must_change_password" class="sub">待改密</div>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template #default="{ row }">{{ fmtTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="220" align="center">
        <template #default="{ row }">
          <el-button link type="primary" @click="resetPwd(row)">重置密码</el-button>
          <el-button link :type="row.is_active ? 'warning' : 'success'" @click="toggleActive(row)">{{ row.is_active ? '禁用' : '启用' }}</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" title="新增用户" width="420px">
      <el-form label-position="top">
        <el-form-item label="用户名"><el-input v-model="form.username" /></el-form-item>
        <el-form-item label="初始密码"><el-input v-model="form.password" show-password /></el-form-item>
        <el-form-item label="角色">
          <el-radio-group v-model="form.role">
            <el-radio value="member">成员</el-radio><el-radio value="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="save">创建</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { userApi } from '../../api'

const rows = ref([])
const loading = ref(false)
const visible = ref(false)
const form = ref({ username: '', password: '', role: 'member' })

function fmtTime(t) { return t ? new Date(t).toLocaleString() : '' }
async function load() { loading.value = true; try { rows.value = await userApi.list() } finally { loading.value = false } }
function open() { form.value = { username: '', password: '', role: 'member' }; visible.value = true }

async function save() {
  if (form.value.username.length < 2) return ElMessage.warning('用户名至少2位')
  if (form.value.password.length < 6) return ElMessage.warning('密码至少6位')
  await userApi.create(form.value)
  ElMessage.success('已创建，首次登录需改密'); visible.value = false; load()
}
async function resetPwd(row) {
  const { value } = await ElMessageBox.prompt(`为「${row.username}」设置新密码`, '重置密码', { confirmButtonText: '确定', cancelButtonText: '取消' })
  if (!value) return
  await userApi.update(row.id, { password: value }); ElMessage.success('已重置')
}
async function toggleActive(row) { await userApi.update(row.id, { is_active: !row.is_active }); load() }
async function remove(row) {
  await ElMessageBox.confirm(`删除用户「${row.username}」？`, '确认', { type: 'warning' })
  await userApi.remove(row.id); ElMessage.success('已删除'); load()
}
onMounted(load)
</script>

<style scoped>
.panel-title { display: flex; align-items: center; gap: 9px; font-weight: 600; }
.panel-title .bar { width: 4px; height: 16px; border-radius: 2px; background: linear-gradient(to bottom, #e5323c, #c7000b); }
.sub { color: var(--el-color-warning); font-size: 12px; }
</style>
