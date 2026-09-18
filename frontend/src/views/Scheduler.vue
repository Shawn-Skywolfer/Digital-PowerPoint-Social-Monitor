<template>
  <div>
    <el-row :gutter="16">
      <el-col :span="13">
        <el-card shadow="never" class="panel">
          <template #header>
            <div class="card-headbar"><div class="panel-title"><span class="bar"></span>定时抓取任务</div>
              <el-button type="primary" size="small" :icon="Plus" @click="openJob()">新建任务</el-button></div>
          </template>
          <el-table :data="jobs" v-loading="loading" size="small">
            <el-table-column prop="name" label="名称" min-width="130" show-overflow-tooltip />
            <el-table-column prop="cron" label="Cron" width="110">
              <template #default="{ row }"><code>{{ row.cron }}</code></template>
            </el-table-column>
            <el-table-column label="下次运行" width="150">
              <template #default="{ row }">{{ fmtTime(row.next_run) }}</template>
            </el-table-column>
            <el-table-column label="排名" width="70" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.ranking_enabled" size="small" type="success" effect="plain">{{ row.ranking_metric }}</el-tag>
                <span v-else class="sub">—</span>
              </template>
            </el-table-column>
            <el-table-column label="启用" width="70" align="center">
              <template #default="{ row }">
                <el-switch :model-value="row.enabled" @change="v => toggleJob(row, v)" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" align="center">
              <template #default="{ row }">
                <el-button link type="primary" @click="runNow(row)">运行</el-button>
                <el-button link type="primary" @click="openJob(row)">编辑</el-button>
                <el-button link type="danger" @click="removeJob(row)">删</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="cron-help">Cron 5段：分 时 日 月 周。例：<code>0 8 * * *</code> 每天8点；<code>0 8 * * 1</code> 每周一8点</div>
        </el-card>

        <!-- 历史报告 -->
        <el-card shadow="never" class="panel" style="margin-top:16px">
          <template #header>
            <div class="panel-title"><span class="bar"></span>排名报告（日报 / 周报）</div>
          </template>
          <el-collapse v-if="reports.length">
            <el-collapse-item v-for="r in reports" :key="r.id" :name="r.id">
              <template #title>
                <span>报告 #{{ r.id }} · {{ r.metric }} · {{ fmtTime(r.created_at) }}</span>
              </template>
              <el-table :data="r.items" size="small">
                <el-table-column type="index" label="#" width="50" />
                <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
                <el-table-column prop="account_name" label="公众号" width="140" />
                <el-table-column prop="read_num" label="阅读" width="90" align="right" />
                <el-table-column prop="like_num" label="点赞" width="80" align="right" />
              </el-table>
            </el-collapse-item>
          </el-collapse>
          <el-empty v-else description="暂无报告，运行任务后生成" :image-size="80" />
        </el-card>
      </el-col>

      <!-- 实时排名 -->
      <el-col :span="11">
        <el-card shadow="never" class="panel">
          <template #header>
            <div class="card-headbar"><div class="panel-title"><span class="bar"></span>实时阅读排名</div>
              <div class="actions">
                <el-select v-model="rkDays" size="small" style="width:110px" @change="loadRanking">
                  <el-option label="近3天" :value="3" /><el-option label="近7天" :value="7" />
                  <el-option label="近30天" :value="30" />
                </el-select>
                <el-button size="small" :icon="Refresh" circle @click="loadRanking" />
              </div>
            </div>
          </template>
          <el-table :data="ranking" size="small" max-height="600" v-loading="loadingRank">
            <el-table-column type="index" label="#" width="46" />
            <el-table-column label="标题" min-width="200">
              <template #default="{ row }">
                <el-link type="primary" @click="$router.push(`/articles/${row.article_id}`)">{{ row.title }}</el-link>
                <div class="sub">{{ row.account_name }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="read_num" label="阅读" width="90" align="right" sortable />
            <el-table-column prop="like_num" label="点赞" width="80" align="right" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 任务编辑 -->
    <el-dialog v-model="jobVisible" :title="jobForm.id ? '编辑任务' : '新建定时任务'" width="520px">
      <el-form label-position="top">
        <el-form-item label="任务名称"><el-input v-model="jobForm.name" /></el-form-item>
        <el-form-item label="公众号">
          <el-select v-model="jobForm.account_ids" multiple filterable style="width:100%">
            <el-option v-for="a in accounts" :key="a.id" :label="a.name" :value="a.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Cron 表达式"><el-input v-model="jobForm.cron" placeholder="0 8 * * *" /></el-form-item>
        <el-form-item label="抓取字段">
          <el-checkbox-group v-model="jobForm.fields">
            <el-checkbox v-for="f in allFields" :key="f.value" :value="f.value">{{ f.label }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="jobForm.ranking_enabled">生成阅读排名报告</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="jobVisible = false">取消</el-button>
        <el-button type="primary" @click="saveJob">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus } from '@element-plus/icons-vue'
import { accountApi, schedulerApi } from '../api'

const jobs = ref([])
const reports = ref([])
const ranking = ref([])
const accounts = ref([])
const loading = ref(false)
const loadingRank = ref(false)
const rkDays = ref(7)
const jobVisible = ref(false)
const jobForm = ref({ id: null, name: '', account_ids: [], cron: '0 8 * * *', fields: ['title', 'publish_time', 'read_num'], ranking_enabled: true, ranking_metric: 'read_num', enabled: true })

const allFields = [
  { value: 'title', label: '标题' }, { value: 'publish_time', label: '发布时间' }, { value: 'content', label: '正文' },
  { value: 'read_num', label: '阅读' }, { value: 'like_num', label: '点赞' }, { value: 'wow_num', label: '在看' },
  { value: 'share_num', label: '转发' }, { value: 'collect_num', label: '收藏' }, { value: 'comment', label: '评论' },
]

function fmtTime(t) { return t ? new Date(t).toLocaleString() : '' }

async function loadJobs() {
  loading.value = true
  try {
    jobs.value = await schedulerApi.jobs()
    reports.value = await schedulerApi.reports({ limit: 10 })
  } finally { loading.value = false }
}
async function loadRanking() {
  loadingRank.value = true
  try { ranking.value = (await schedulerApi.ranking({ metric: 'read_num', days: rkDays.value, limit: 50 })).items || [] }
  finally { loadingRank.value = false }
}

function openJob(j) {
  jobForm.value = j ? { id: j.id, name: j.name, account_ids: [...j.account_ids], cron: j.cron, fields: [...j.fields], ranking_enabled: j.ranking_enabled, ranking_metric: j.ranking_metric, enabled: j.enabled }
    : { id: null, name: '', account_ids: [], cron: '0 8 * * *', fields: ['title', 'publish_time', 'read_num'], ranking_enabled: true, ranking_metric: 'read_num', enabled: true }
  jobVisible.value = true
}
async function saveJob() {
  const f = jobForm.value
  if (!f.name || !f.account_ids.length) return ElMessage.warning('请填写名称并选择公众号')
  const payload = { name: f.name, account_ids: f.account_ids, cron: f.cron, fields: f.fields, ranking_enabled: f.ranking_enabled, ranking_metric: f.ranking_metric, enabled: f.enabled }
  if (f.id) await schedulerApi.update(f.id, payload)
  else await schedulerApi.create(payload)
  ElMessage.success('已保存'); jobVisible.value = false; loadJobs()
}
async function toggleJob(row, v) {
  await schedulerApi.update(row.id, { name: row.name, account_ids: row.account_ids, cron: row.cron, fields: row.fields, ranking_enabled: row.ranking_enabled, ranking_metric: row.ranking_metric, enabled: v })
  row.enabled = v
}
async function runNow(row) { await schedulerApi.run(row.id); ElMessage.success('已触发，稍后查看报告'); setTimeout(loadJobs, 2000) }
async function removeJob(row) {
  await ElMessageBox.confirm(`删除任务「${row.name}」？`, '确认', { type: 'warning' })
  await schedulerApi.remove(row.id); ElMessage.success('已删除'); loadJobs()
}

onMounted(async () => {
  accounts.value = await accountApi.list()
  loadJobs(); loadRanking()
})
</script>

<style scoped>
.panel-title { display: flex; align-items: center; gap: 9px; font-weight: 600; }
.panel-title .bar { width: 4px; height: 16px; border-radius: 2px; background: linear-gradient(to bottom, #e5323c, #c7000b); }
.sub { color: var(--ink-400); font-size: 12px; }
.cron-help { color: var(--ink-400); font-size: 12px; margin-top: 10px; }
code {
  background: var(--ink-100); padding: 2px 7px; border-radius: 5px;
  font-family: 'JetBrains Mono', Consolas, monospace; font-size: 12px;
  color: var(--ink-700);
}
</style>
