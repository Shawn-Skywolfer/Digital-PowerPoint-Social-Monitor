<template>
  <div>
    <el-row :gutter="16">
      <!-- 抓取配置 -->
      <el-col :span="10">
        <el-card shadow="never" class="panel">
          <template #header>
            <div class="card-headbar">
              <div class="panel-title"><span class="bar"></span>发起抓取</div>
              <span class="text-sub">配置公众号与字段，后台自动执行</span>
            </div>
          </template>
          <el-form label-position="top">
            <el-form-item label="按分组选择（快捷整组加入）">
              <el-select v-model="form.group_ids" multiple placeholder="选择分组，组内公众号全部加入" style="width:100%" @change="applyGroups">
                <el-option v-for="g in groups" :key="g.id" :label="`${g.name}（${g.account_count}个）`" :value="g.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="选择公众号">
              <el-select v-model="form.account_ids" multiple filterable placeholder="选择要抓取的公众号" style="width:100%">
                <el-option v-for="a in accounts" :key="a.id" :label="a.name" :value="a.id" />
              </el-select>
              <el-checkbox v-model="allMonitoring" @change="toggleAll" style="margin-top:6px">全选监测中的公众号</el-checkbox>
            </el-form-item>
            <el-form-item label="时间范围（按文章发布时间）">
              <el-date-picker v-model="range" type="datetimerange" range-separator="至"
                start-placeholder="开始" end-placeholder="结束" style="width:100%" />
            </el-form-item>
            <el-form-item label="抓取字段（点选）">
              <div class="field-row" v-for="g in fieldGroups" :key="g.label">
                <span class="group-label">{{ g.label }}</span>
                <el-checkbox-group v-model="form.fields">
                  <el-checkbox v-for="f in g.fields" :key="f.value" :value="f.value">{{ f.label }}</el-checkbox>
                </el-checkbox-group>
              </div>
            </el-form-item>
            <el-form-item label="抓取方案（可保存复用）">
              <div style="display:flex; gap:8px; width:100%">
                <el-select v-model="profileId" placeholder="选择方案自动填充" clearable style="flex:1" @change="applyProfile">
                  <el-option v-for="p in profiles" :key="p.id" :label="p.name" :value="p.id" />
                </el-select>
                <el-button @click="saveProfile">存为方案</el-button>
              </div>
            </el-form-item>
            <el-button type="primary" :loading="starting" style="width:100%" @click="start">
              开始抓取{{ form.account_ids.length ? `（${form.account_ids.length} 个公众号）` : '' }}
            </el-button>
          </el-form>
        </el-card>
      </el-col>

      <!-- 任务列表 -->
      <el-col :span="14">
        <el-card shadow="never" class="panel">
          <template #header>
            <div class="card-headbar">
              <div class="panel-title">
                <span class="bar"></span>抓取任务
                <span v-if="tasks.length" class="text-sub">每 4 秒自动刷新</span>
              </div>
              <el-button size="small" :icon="Refresh" circle @click="loadTasks" />
            </div>
          </template>
          <el-table :data="tasks" v-loading="loadingTasks" size="small">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column label="进度" min-width="150">
              <template #default="{ row }">
                <el-progress :percentage="row.progress" :status="statusType(row.status)" />
                <div class="task-sub">{{ row.done_items }}/{{ row.total_items }} · 新增{{ row.new_articles }} 更新{{ row.updated_articles }}</div>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="90" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
                <div v-if="row.reviews_created" class="task-sub">待确认{{ row.reviews_created }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="发起时间" width="150">
              <template #default="{ row }">{{ fmtTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="170" align="center">
              <template #default="{ row }">
                <el-button link type="primary" @click="showLog(row)">日志</el-button>
                <el-button v-if="row.status==='running'||row.status==='pending'" link type="warning" @click="cancel(row)">取消</el-button>
                <el-button link type="danger" @click="removeTask(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="logVisible" :title="`任务 #${logTask?.id} 日志`" width="600px">
      <el-alert v-if="logTask?.error" type="error" :title="logTask.error" :closable="false" style="margin-bottom:10px" />
      <pre class="log-box">{{ logTask?.log || '暂无日志' }}</pre>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { accountApi, fetchApi } from '../api'

const accounts = ref([])
const groups = ref([])
const profiles = ref([])
const profileId = ref(null)
const allMonitoring = ref(false)
const range = ref(null)
const starting = ref(false)
const form = ref({ account_ids: [], group_ids: [], fields: ['title', 'publish_time', 'read_num'] })
const tasks = ref([])
const loadingTasks = ref(false)
const logVisible = ref(false)
const logTask = ref(null)
let timer = null

const fieldGroups = [
  { label: '基础', fields: [{ value: 'title', label: '标题' }, { value: 'publish_time', label: '发布时间' }, { value: 'content', label: '正文' }] },
  { label: '指标', fields: [{ value: 'read_num', label: '阅读量' }, { value: 'like_num', label: '点赞' }, { value: 'wow_num', label: '在看' }, { value: 'share_num', label: '转发' }, { value: 'collect_num', label: '收藏' }] },
  { label: '互动', fields: [{ value: 'comment', label: '评论内容' }] },
]

function toggleAll(v) {
  form.value.account_ids = v ? accounts.value.filter(a => a.is_monitoring).map(a => a.id) : []
}
// 选中分组 → 组内公众号并入手选列表（后端同样会做并集，双保险）
function applyGroups() {
  const gidSet = new Set(form.value.group_ids)
  const inGroups = accounts.value.filter(a => a.group_id && gidSet.has(a.group_id)).map(a => a.id)
  form.value.account_ids = [...new Set([...form.value.account_ids, ...inGroups])]
}
function applyProfile(id) {
  const p = profiles.value.find(x => x.id === id)
  if (p) form.value.fields = [...p.fields]
}
async function saveProfile() {
  const { value } = await ElMessageBox.prompt('方案名称', '保存抓取方案', { confirmButtonText: '保存', cancelButtonText: '取消' })
  if (!value) return
  await fetchApi.createProfile({ name: value, fields: form.value.fields })
  ElMessage.success('已保存')
  profiles.value = await fetchApi.profiles()
}

async function start() {
  if (!form.value.account_ids.length) return ElMessage.warning('请选择公众号')
  if (!form.value.fields.length) return ElMessage.warning('请勾选字段')
  starting.value = true
  try {
    const payload = {
      account_ids: form.value.account_ids,
      group_ids: form.value.group_ids,
      fields: form.value.fields,
      time_start: range.value?.[0] ? range.value[0].toISOString() : undefined,
      time_end: range.value?.[1] ? range.value[1].toISOString() : undefined,
    }
    await fetchApi.createTask(payload)
    ElMessage.success('任务已创建，后台抓取中')
    loadTasks()
  } finally { starting.value = false }
}

function statusType(s) {
  return { success: 'success', failed: 'exception', cancelled: 'info', running: undefined, pending: undefined }[s]
}
function statusText(s) {
  return { success: '成功', failed: '失败', cancelled: '已取消', running: '进行中', pending: '排队中' }[s] || s
}
function fmtTime(t) { return t ? new Date(t).toLocaleString() : '' }

async function loadTasks() {
  loadingTasks.value = true
  try { tasks.value = await fetchApi.tasks() }
  finally { loadingTasks.value = false }
}
async function cancel(row) { await fetchApi.cancel(row.id); ElMessage.success('已取消'); loadTasks() }
async function removeTask(row) {
  const running = row.status === 'running' || row.status === 'pending'
  await ElMessageBox.confirm(
    running ? '任务正在进行中，删除会先取消任务。删除后任务记录不可恢复（已抓取的文章数据保留）。继续？'
            : '删除该任务记录？已抓取的文章数据会保留。', '确认删除', { type: 'warning' })
  await fetchApi.removeTask(row.id)
  ElMessage.success('已删除')
  loadTasks()
}
function showLog(row) { logTask.value = row; logVisible.value = true }

onMounted(async () => {
  [accounts.value, groups.value] = await Promise.all([accountApi.list(), accountApi.groups()])
  profiles.value = await fetchApi.profiles()
  loadTasks()
  timer = setInterval(loadTasks, 4000)  // 轮询进度
})
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.panel-title { display: flex; align-items: center; gap: 9px; font-weight: 600; }
.panel-title .bar { width: 4px; height: 16px; border-radius: 2px; background: linear-gradient(to bottom, #e5323c, #c7000b); }
.field-row { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 4px; }
.group-label { color: var(--ink-400); font-size: 13px; width: 36px; line-height: 24px; flex-shrink: 0; }
.task-sub { color: var(--ink-400); font-size: 12px; margin-top: 2px; }
.log-box {
  background: #101726; color: #b7f0c5;
  padding: 14px; border-radius: 10px;
  max-height: 400px; overflow: auto;
  white-space: pre-wrap; word-break: break-all;
  font-size: 12.5px; line-height: 1.7;
  font-family: 'JetBrains Mono', Consolas, monospace;
}
</style>
