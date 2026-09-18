<template>
  <el-card shadow="never" class="panel">
    <template #header>
      <div class="card-headbar"><div class="panel-title"><span class="bar"></span>云服务配置<span class="text-sub">LightPanda 云端浏览器 / Tavily 检索</span></div>
        <el-button type="primary" @click="open()">新增配置</el-button></div>
    </template>
    <el-table :data="rows" v-loading="loading">
      <el-table-column label="服务" width="130">
        <template #default="{ row }">
          <el-tag size="small" :type="row.service === 'tavily' ? 'success' : 'primary'" effect="plain">{{ row.service }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="名称" min-width="140" />
      <el-table-column prop="base_url" label="Base URL" min-width="200" show-overflow-tooltip />
      <el-table-column prop="api_key_masked" label="Key" width="150" />
      <el-table-column label="启用" width="80" align="center">
        <template #default="{ row }"><el-switch :model-value="row.enabled" @change="v => toggle(row, v)" /></template>
      </el-table-column>
      <el-table-column label="操作" width="180" align="center">
        <template #default="{ row }">
          <el-button link type="primary" @click="test(row)">测试</el-button>
          <el-button link type="primary" @click="open(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-alert type="info" :closable="false" style="margin-top:12px">
      首版交付「配置 + 凭证管理 + 连通性测试」。基于 LightPanda/Tavily 的全网/定点热词检索属后续扩展，经 provider 接口接入。
    </el-alert>

    <el-dialog v-model="visible" :title="form.id ? '编辑配置' : '新增配置'" width="480px">
      <el-form label-position="top">
        <el-form-item label="服务类型">
          <el-select v-model="form.service" :disabled="!!form.id" style="width:100%">
            <el-option label="LightPanda 云端浏览器" value="lightpanda" />
            <el-option label="Tavily 检索" value="tavily" />
          </el-select>
        </el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item v-if="form.service === 'lightpanda'" label="Base URL"><el-input v-model="form.base_url" placeholder="wss://..." /></el-form-item>
        <el-form-item :label="form.id ? 'API Key（留空则不修改）' : 'API Key'"><el-input v-model="form.api_key" show-password /></el-form-item>
        <el-form-item label="额外配置 (JSON，可选)"><el-input v-model="extraText" type="textarea" :rows="2" /></el-form-item>
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
import { serviceApi } from '../../api'

const rows = ref([])
const loading = ref(false)
const visible = ref(false)
const extraText = ref('')
const form = ref({ id: null, service: 'tavily', name: '', base_url: '', api_key: '' })

async function load() { loading.value = true; try { rows.value = await serviceApi.list() } finally { loading.value = false } }
function open(row) {
  form.value = row ? { id: row.id, service: row.service, name: row.name, base_url: row.base_url || '', api_key: '' } : { id: null, service: 'tavily', name: '', base_url: '', api_key: '' }
  extraText.value = row?.extra ? JSON.stringify(row.extra) : ''
  visible.value = true
}
async function save() {
  const f = form.value
  if (!f.name) return ElMessage.warning('请填写名称')
  let extra
  try { extra = extraText.value ? JSON.parse(extraText.value) : undefined } catch { return ElMessage.error('JSON 格式错误') }
  if (f.id) {
    const payload = { name: f.name, base_url: f.base_url || undefined, extra }
    if (f.api_key) payload.api_key = f.api_key
    await serviceApi.update(f.id, payload)
  } else await serviceApi.create({ service: f.service, name: f.name, base_url: f.base_url || undefined, api_key: f.api_key, extra })
  ElMessage.success('已保存'); visible.value = false; load()
}
async function toggle(row, v) { await serviceApi.update(row.id, { enabled: v }); row.enabled = v }
async function test(row) {
  try { const r = await serviceApi.test(row.id); r.ok ? ElMessage.success('连接成功：' + r.message) : ElMessage.error('失败：' + r.message) }
  catch { /* 已提示 */ }
}
async function remove(row) {
  await ElMessageBox.confirm(`删除「${row.name}」？`, '确认', { type: 'warning' })
  await serviceApi.remove(row.id); ElMessage.success('已删除'); load()
}
onMounted(load)
</script>

<style scoped>
.panel-title { display: flex; align-items: center; gap: 9px; font-weight: 600; }
.panel-title .bar { width: 4px; height: 16px; border-radius: 2px; background: linear-gradient(to bottom, #e5323c, #c7000b); }
</style>
