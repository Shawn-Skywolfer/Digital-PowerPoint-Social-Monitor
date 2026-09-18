<template>
  <el-card shadow="never" class="panel">
    <template #header>
      <div class="card-headbar">
        <div class="panel-title"><span class="bar"></span>MCP 服务器配置
          <span class="text-sub">如 FireCrawl</span>
          <el-tag v-if="mcpAvailable === false" type="warning" size="small">未安装 mcp SDK</el-tag>
        </div>
        <el-button type="primary" @click="open()">新增服务器</el-button>
      </div>
    </template>
    <el-table :data="rows" v-loading="loading">
      <el-table-column prop="name" label="名称" min-width="140" />
      <el-table-column prop="transport" label="传输" width="90">
        <template #default="{ row }"><el-tag size="small" effect="plain">{{ row.transport }}</el-tag></template>
      </el-table-column>
      <el-table-column label="连接" min-width="240">
        <template #default="{ row }">
          <span class="conn">{{ row.transport === 'stdio' ? (row.command + ' ' + (row.args || []).join(' ')) : row.url }}</span>
        </template>
      </el-table-column>
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

    <el-dialog v-model="visible" :title="form.id ? '编辑 MCP 服务器' : '新增 MCP 服务器'" width="540px">
      <el-form label-position="top">
        <el-form-item label="名称"><el-input v-model="form.name" placeholder="如：FireCrawl" /></el-form-item>
        <el-form-item label="传输方式">
          <el-radio-group v-model="form.transport">
            <el-radio value="stdio">stdio（本地命令）</el-radio>
            <el-radio value="sse">sse</el-radio>
            <el-radio value="http">http</el-radio>
          </el-radio-group>
        </el-form-item>
        <template v-if="form.transport === 'stdio'">
          <el-form-item label="命令"><el-input v-model="form.command" placeholder="npx / python / 可执行文件" /></el-form-item>
          <el-form-item label="参数（每行一个）"><el-input v-model="argsText" type="textarea" :rows="3" placeholder="-y&#10;firecrawl-mcp" /></el-form-item>
          <el-form-item label="环境变量 (JSON)"><el-input v-model="envText" type="textarea" :rows="2" placeholder='{"FIRECRAWL_API_KEY":"..."}' /></el-form-item>
        </template>
        <template v-else>
          <el-form-item label="URL"><el-input v-model="form.url" placeholder="https://.../sse" /></el-form-item>
          <el-form-item label="请求头 (JSON)"><el-input v-model="headersText" type="textarea" :rows="2" placeholder='{"Authorization":"Bearer ..."}' /></el-form-item>
        </template>
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
import { mcpApi } from '../../api'

const rows = ref([])
const loading = ref(false)
const visible = ref(false)
const mcpAvailable = ref(null)
const form = ref({ id: null, name: '', transport: 'sse', command: '', url: '', note: '' })
const argsText = ref('')
const envText = ref('')
const headersText = ref('')

async function load() {
  loading.value = true
  try {
    rows.value = await mcpApi.list()
    try { mcpAvailable.value = (await mcpApi.available()).available } catch { mcpAvailable.value = null }
  } finally { loading.value = false }
}
function open(row) {
  form.value = row ? { id: row.id, name: row.name, transport: row.transport, command: row.command || '', url: row.url || '', note: row.note || '' } : { id: null, name: '', transport: 'sse', command: '', url: '', note: '' }
  argsText.value = (row?.args || []).join('\n')
  envText.value = ''
  headersText.value = ''
  visible.value = true
}
async function save() {
  const f = form.value
  if (!f.name) return ElMessage.warning('请填写名称')
  let env, headers
  try {
    env = envText.value ? JSON.parse(envText.value) : undefined
    headers = headersText.value ? JSON.parse(headersText.value) : undefined
  } catch { return ElMessage.error('JSON 格式错误') }
  const args = argsText.value ? argsText.value.split('\n').map(s => s.trim()).filter(Boolean) : undefined
  const payload = { name: f.name, transport: f.transport, command: f.command || undefined, args, env, url: f.url || undefined, headers, note: f.note }
  if (f.id) await mcpApi.update(f.id, payload)
  else await mcpApi.create(payload)
  ElMessage.success('已保存'); visible.value = false; load()
}
async function toggle(row, v) { await mcpApi.update(row.id, { enabled: v }); row.enabled = v }
async function test(row) {
  try { const r = await mcpApi.test(row.id); r.ok ? ElMessage.success('连接成功：' + r.message) : ElMessage.error('失败：' + r.message) }
  catch { /* 已提示 */ }
}
async function remove(row) {
  await ElMessageBox.confirm(`删除「${row.name}」？`, '确认', { type: 'warning' })
  await mcpApi.remove(row.id); ElMessage.success('已删除'); load()
}
onMounted(load)
</script>

<style scoped>
.panel-title { display: flex; align-items: center; gap: 9px; font-weight: 600; }
.panel-title .bar { width: 4px; height: 16px; border-radius: 2px; background: linear-gradient(to bottom, #e5323c, #c7000b); }
.conn { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 12px; color: var(--ink-500); }
</style>
