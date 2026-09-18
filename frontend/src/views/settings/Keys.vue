<template>
  <el-card shadow="never" class="panel">
    <template #header>
      <div class="card-headbar"><div class="panel-title"><span class="bar"></span>dajiala API Key 池<span class="text-sub">按用户绑定，失败自动切换</span></div>
        <el-button type="primary" @click="open()">新增 Key</el-button></div>
    </template>
    <el-table :data="rows" v-loading="loading">
      <el-table-column prop="label" label="备注名" min-width="130" />
      <el-table-column prop="key_masked" label="Key" width="150" />
      <el-table-column label="归属" width="110">
        <template #default="{ row }">{{ row.owner_id ? '用户#' + row.owner_id : '全局' }}</template>
      </el-table-column>
      <el-table-column label="用量" width="140">
        <template #default="{ row }">
          <span>{{ row.used }}{{ row.quota ? ' / ' + row.quota : '' }}</span>
          <el-progress v-if="row.quota" :percentage="Math.min(100, Math.round(row.used / row.quota * 100))" :show-text="false" style="margin-top:4px" />
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag size="small" :type="{ ok: 'success', quota_exceeded: 'warning', invalid: 'danger', unknown: 'info' }[row.status] || 'info'">
            {{ { ok: '正常', quota_exceeded: '配额尽', invalid: '失效', unknown: '未校验' }[row.status] || row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="默认" width="70" align="center">
        <template #default="{ row }"><el-tag v-if="row.is_default" size="small" type="success">默认</el-tag></template>
      </el-table-column>
      <el-table-column label="启用" width="80" align="center">
        <template #default="{ row }"><el-switch :model-value="row.enabled" @change="v => toggle(row, v)" /></template>
      </el-table-column>
      <el-table-column label="操作" width="180" align="center">
        <template #default="{ row }">
          <el-button link type="primary" @click="check(row)">校验</el-button>
          <el-button link type="primary" @click="open(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" :title="form.id ? '编辑 Key' : '新增 Key'" width="460px">
      <el-form label-position="top">
        <el-form-item label="备注名"><el-input v-model="form.label" placeholder="如：主账号 / 备用" /></el-form-item>
        <el-form-item :label="form.id ? 'Key（留空则不修改）' : 'Key'"><el-input v-model="form.key" show-password /></el-form-item>
        <el-form-item label="配额（积分上限，可选）"><el-input-number v-model="form.quota" :min="0" style="width:100%" /></el-form-item>
        <el-form-item><el-checkbox v-model="form.is_default">设为默认 Key</el-checkbox></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.note" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { keyApi } from '../../api'

const rows = ref([])
const loading = ref(false)
const visible = ref(false)
const form = ref({ id: null, label: '', key: '', quota: null, is_default: false, note: '' })

async function load() { loading.value = true; try { rows.value = await keyApi.list() } finally { loading.value = false } }
function open(row) {
  form.value = row ? { id: row.id, label: row.label, key: '', quota: row.quota, is_default: row.is_default, note: row.note || '' } : { id: null, label: '', key: '', quota: null, is_default: false, note: '' }
  visible.value = true
}
async function save() {
  const f = form.value
  if (!f.label) return ElMessage.warning('请填写备注名')
  if (!f.id && !f.key) return ElMessage.warning('请填写 Key')
  if (f.id) {
    const payload = { label: f.label, quota: f.quota, is_default: f.is_default, note: f.note }
    if (f.key) payload.key = f.key
    await keyApi.update(f.id, payload)
  } else await keyApi.create({ label: f.label, key: f.key, quota: f.quota, is_default: f.is_default, note: f.note })
  ElMessage.success('已保存'); visible.value = false; load()
}
async function toggle(row, v) { await keyApi.update(row.id, { enabled: v }); row.enabled = v }
async function check(row) {
  try { const r = await keyApi.check(row.id); r.ok ? ElMessage.success('Key 有效：' + r.message) : ElMessage.error('校验失败：' + r.message); load() }
  catch { /* 已提示 */ }
}
async function remove(row) {
  await ElMessageBox.confirm(`删除 Key「${row.label}」？`, '确认', { type: 'warning' })
  await keyApi.remove(row.id); ElMessage.success('已删除'); load()
}
onMounted(load)
</script>

<style scoped>
.panel-title { display: flex; align-items: center; gap: 9px; font-weight: 600; }
.panel-title .bar { width: 4px; height: 16px; border-radius: 2px; background: linear-gradient(to bottom, #e5323c, #c7000b); }
</style>
