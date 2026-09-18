<template>
  <el-card shadow="never" class="panel">
    <template #header>
      <div class="card-headbar"><div class="panel-title"><span class="bar"></span>大模型配置<span class="text-sub">OpenAI 兼容协议</span></div>
        <el-button type="primary" @click="open()">新增模型</el-button></div>
    </template>
    <el-table :data="rows" v-loading="loading">
      <el-table-column prop="name" label="名称" min-width="140" />
      <el-table-column prop="provider" label="服务商" width="110" />
      <el-table-column prop="model" label="模型" min-width="160" show-overflow-tooltip />
      <el-table-column prop="base_url" label="Base URL" min-width="200" show-overflow-tooltip />
      <el-table-column prop="api_key_masked" label="Key" width="130" />
      <el-table-column label="启用" width="80" align="center">
        <template #default="{ row }"><el-switch :model-value="row.enabled" @change="v => toggle(row, v)" /></template>
      </el-table-column>
      <el-table-column label="操作" width="190" align="center">
        <template #default="{ row }">
          <el-button link type="primary" @click="test(row)">测试</el-button>
          <el-button link type="primary" @click="open(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="visible" :title="form.id ? '编辑模型' : '新增模型'" width="520px">
      <el-form label-position="top">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="服务商">
          <el-select v-model="form.provider" style="width:100%">
            <el-option label="OpenAI / 兼容" value="openai" />
            <el-option label="Azure OpenAI" value="azure" />
            <el-option label="其他兼容端点" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="Base URL"><el-input v-model="form.base_url" placeholder="https://api.openai.com/v1" /></el-form-item>
        <el-form-item :label="form.id ? 'API Key（留空则不修改）' : 'API Key'"><el-input v-model="form.api_key" show-password /></el-form-item>
        <el-form-item label="模型名"><el-input v-model="form.model" placeholder="gpt-4o-mini / qwen-plus / ..." /></el-form-item>
        <el-form-item label="额外参数 (JSON，可选)"><el-input v-model="paramsText" type="textarea" :rows="2" placeholder='{"temperature":0.7}' /></el-form-item>
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
import { llmApi } from '../../api'

const rows = ref([])
const loading = ref(false)
const visible = ref(false)
const paramsText = ref('')
const form = ref({ id: null, name: '', provider: 'openai', base_url: '', api_key: '', model: '' })

async function load() { loading.value = true; try { rows.value = await llmApi.list() } finally { loading.value = false } }
function open(row) {
  form.value = row ? { id: row.id, name: row.name, provider: row.provider, base_url: row.base_url, api_key: '', model: row.model } : { id: null, name: '', provider: 'openai', base_url: '', api_key: '', model: '' }
  paramsText.value = row?.params ? JSON.stringify(row.params) : ''
  visible.value = true
}
async function save() {
  const f = form.value
  if (!f.name || !f.base_url || !f.model) return ElMessage.warning('请填写名称/URL/模型')
  let params
  try { params = paramsText.value ? JSON.parse(paramsText.value) : undefined } catch { return ElMessage.error('参数 JSON 格式错误') }
  if (f.id) {
    const payload = { name: f.name, provider: f.provider, base_url: f.base_url, model: f.model, params }
    if (f.api_key) payload.api_key = f.api_key
    await llmApi.update(f.id, payload)
  } else await llmApi.create({ name: f.name, provider: f.provider, base_url: f.base_url, api_key: f.api_key, model: f.model, params })
  ElMessage.success('已保存'); visible.value = false; load()
}
async function toggle(row, v) { await llmApi.update(row.id, { enabled: v }); row.enabled = v }
async function test(row) {
  try { const r = await llmApi.test(row.id); r.ok ? ElMessage.success('连接成功：' + r.message) : ElMessage.error('失败：' + r.message) }
  catch { /* 拦截器已提示 */ }
}
async function remove(row) {
  await ElMessageBox.confirm(`删除模型「${row.name}」？`, '确认', { type: 'warning' })
  await llmApi.remove(row.id); ElMessage.success('已删除'); load()
}
onMounted(load)
</script>

<style scoped>
.panel-title { display: flex; align-items: center; gap: 9px; font-weight: 600; }
.panel-title .bar { width: 4px; height: 16px; border-radius: 2px; background: linear-gradient(to bottom, #e5323c, #c7000b); }
</style>
