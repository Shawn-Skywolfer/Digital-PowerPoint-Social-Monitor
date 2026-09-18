<template>
  <div>
    <el-card shadow="never" class="panel">
      <div class="toolbar">
        <div class="filters">
          <el-select v-model="filterGroup" placeholder="按分组筛选" clearable style="width:180px">
            <el-option :value="0" label="未分组" />
            <el-option v-for="g in groups" :key="g.id" :label="`${g.name}（${g.account_count}）`" :value="g.id" />
          </el-select>
          <el-input v-model="filterKeyword" placeholder="搜索名称 / 标签" clearable style="width:210px" :prefix-icon="Search" />
          <span class="count-hint">共 {{ filteredAccounts.length }} 个公众号</span>
        </div>
        <div class="actions">
          <el-button :icon="Folder" @click="openGroupMgr">分组管理</el-button>
          <el-button type="primary" :icon="Plus" @click="openSearch">在线检索添加</el-button>
          <el-button type="success" plain :icon="Upload" @click="importVisible = true">批量导入</el-button>
          <el-button :icon="Refresh" circle @click="load" />
        </div>
      </div>

      <!-- 批量操作条 -->
      <transition name="el-fade-in">
        <div v-if="selected.length" class="batch-bar">
          <span class="sel-info">已选 <b>{{ selected.length }}</b> 个公众号</span>
          <el-select v-model="batchGroupId" placeholder="批量设置分组" clearable size="small" style="width:170px">
            <el-option :value="0" label="移出分组" />
            <el-option v-for="g in groups" :key="g.id" :label="g.name" :value="g.id" />
          </el-select>
          <el-button size="small" type="primary" @click="applyBatchGroup">应用</el-button>
        </div>
      </transition>

      <el-table :data="filteredAccounts" v-loading="loading" @selection-change="s => selected = s">
        <el-table-column type="selection" width="42" />
        <el-table-column label="公众号" min-width="220">
          <template #default="{ row }">
            <div class="acc-cell">
              <el-avatar :size="34" :src="row.avatar">{{ (row.name || '?')[0] }}</el-avatar>
              <div>
                <div class="acc-name">{{ row.name }}
                  <el-tag v-if="row.verify" size="small" type="success" effect="plain">{{ row.verify }}</el-tag>
                </div>
                <div class="acc-sub">{{ row.gh_id || row.biz }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="分组" width="130">
          <template #default="{ row }">
            <el-tag v-if="row.group_name" size="small" type="warning" effect="plain">{{ row.group_name }}</el-tag>
            <span v-else class="acc-sub">未分组</span>
          </template>
        </el-table-column>
        <el-table-column prop="article_count" label="文章数" width="90" align="center" />
        <el-table-column prop="tags" label="标签" min-width="120">
          <template #default="{ row }">
            <el-tag v-for="t in (row.tags || '').split(',').filter(Boolean)" :key="t" size="small" class="tag">{{ t }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="监测中" width="90" align="center">
          <template #default="{ row }">
            <el-switch :model-value="row.is_monitoring" @change="v => toggleMonitor(row, v)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="editTags(row)">标签</el-button>
            <el-button link type="primary" @click="openAssign(row)">分组</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 分组管理 -->
    <el-dialog v-model="groupVisible" title="分组管理" width="480px">
      <div style="display:flex; gap:8px; margin-bottom:12px">
        <el-input v-model="newGroupName" placeholder="新分组名称" clearable @keyup.enter="createGroup" />
        <el-button type="primary" :disabled="!newGroupName.trim()" @click="createGroup">新建</el-button>
      </div>
      <el-table :data="groups" size="small" max-height="320">
        <el-table-column prop="name" label="分组名" min-width="140" />
        <el-table-column prop="account_count" label="公众号数" width="90" align="center" />
        <el-table-column label="操作" width="130" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="renameGroup(row)">改名</el-button>
            <el-button link type="danger" @click="removeGroup(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 单账号分配分组 -->
    <el-dialog v-model="assignVisible" :title="`设置分组 · ${assignRow?.name || ''}`" width="380px">
      <el-select v-model="assignGroupId" placeholder="选择分组" clearable style="width:100%">
        <el-option :value="0" label="未分组（移出）" />
        <el-option v-for="g in groups" :key="g.id" :label="g.name" :value="g.id" />
      </el-select>
      <template #footer>
        <el-button @click="assignVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAssign">保存</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入 -->
    <el-dialog v-model="importVisible" title="批量导入公众号" width="560px">
      <el-alert type="info" :closable="false" style="margin-bottom:10px">
        每行一个：公众号名称 / 微信号(gh_id) / 文章或主页链接。导入时会自动检索校验并去重。
      </el-alert>
      <el-input v-model="importText" type="textarea" :rows="8" placeholder="人民日报&#10;华为数字能源&#10;https://mp.weixin.qq.com/..." />
      <div style="display:flex; gap:8px; margin-top:10px">
        <el-input v-model="importTags" placeholder="统一打标签（可选，逗号分隔）" />
        <el-select v-model="importGroupId" placeholder="导入到分组（可选）" clearable style="width:180px">
          <el-option v-for="g in groups" :key="g.id" :label="g.name" :value="g.id" />
        </el-select>
      </div>
      <template #footer>
        <el-button @click="importVisible = false">取消</el-button>
        <el-button type="primary" :loading="importing" @click="doImport">开始导入</el-button>
      </template>
      <el-table v-if="importResult.length" :data="importResult" size="small" max-height="240" style="margin-top:12px">
        <el-table-column prop="input" label="输入" min-width="140" show-overflow-tooltip />
        <el-table-column label="结果" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="row.ok ? 'success' : 'danger'">{{ row.ok ? '成功' : '失败' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="说明" min-width="120" show-overflow-tooltip />
      </el-table>
    </el-dialog>

    <!-- 在线检索 -->
    <el-dialog v-model="searchVisible" title="在线检索公众号" width="620px">
      <div style="display:flex; gap:8px">
        <el-input v-model="searchQuery" placeholder="输入公众号名称关键词" clearable @keyup.enter="doSearch" />
        <el-button type="primary" :loading="searching" @click="doSearch">检索</el-button>
      </div>
      <el-table :data="searchResults" size="small" max-height="360" style="margin-top:12px" v-loading="searching">
        <el-table-column label="名称" min-width="200">
          <template #default="{ row }">
            <div class="acc-cell">
              <el-avatar :size="30" :src="row.avatar">{{ (row.name || '?')[0] }}</el-avatar>
              <div>
                <div>{{ row.name }}</div>
                <div class="acc-sub">{{ row.gh_id }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="intro" label="简介" min-width="180" show-overflow-tooltip />
        <el-table-column label="操作" width="90" align="center">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="addOne(row)">添加</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Refresh, Folder, Search } from '@element-plus/icons-vue'
import { accountApi } from '../api'

const accounts = ref([])
const groups = ref([])
const loading = ref(false)
const filterGroup = ref(null)
const filterKeyword = ref('')
const selected = ref([])
const batchGroupId = ref(null)

const groupVisible = ref(false)
const newGroupName = ref('')
const assignVisible = ref(false)
const assignRow = ref(null)
const assignGroupId = ref(null)

const importVisible = ref(false)
const importText = ref('')
const importTags = ref('')
const importGroupId = ref(null)
const importing = ref(false)
const importResult = ref([])
const searchVisible = ref(false)
const searchQuery = ref('')
const searching = ref(false)
const searchResults = ref([])

const filteredAccounts = computed(() => {
  let list = accounts.value
  if (filterGroup.value === 0) list = list.filter(a => !a.group_id)
  else if (filterGroup.value) list = list.filter(a => a.group_id === filterGroup.value)
  const kw = filterKeyword.value.trim().toLowerCase()
  if (kw) list = list.filter(a => (a.name || '').toLowerCase().includes(kw) || (a.tags || '').toLowerCase().includes(kw))
  return list
})

async function load() {
  loading.value = true
  try { [accounts.value, groups.value] = await Promise.all([accountApi.list(), accountApi.groups()]) }
  finally { loading.value = false }
}

// ---------- 分组 ----------
function openGroupMgr() { groupVisible.value = true }
async function createGroup() {
  const name = newGroupName.value.trim()
  if (!name) return
  try {
    await accountApi.createGroup({ name })
    ElMessage.success('已创建')
    newGroupName.value = ''
    load()
  } catch (e) { /* request 拦截器已提示 */ }
}
async function renameGroup(row) {
  const { value } = await ElMessageBox.prompt('新分组名', `改名 · ${row.name}`, {
    inputValue: row.name, confirmButtonText: '保存', cancelButtonText: '取消',
  })
  if (!value || !value.trim() || value.trim() === row.name) return
  await accountApi.renameGroup(row.id, { name: value.trim() })
  ElMessage.success('已改名')
  load()
}
async function removeGroup(row) {
  await ElMessageBox.confirm(`删除分组「${row.name}」？组内公众号将移出分组（不会被删除）。`, '确认', { type: 'warning' })
  await accountApi.removeGroup(row.id)
  ElMessage.success('已删除')
  load()
}

function openAssign(row) {
  assignRow.value = row
  assignGroupId.value = row.group_id ?? null
  assignVisible.value = true
}
async function saveAssign() {
  await accountApi.update(assignRow.value.id, { group_id: assignGroupId.value ?? 0 })
  ElMessage.success('已保存')
  assignVisible.value = false
  load()
}

async function applyBatchGroup() {
  const ids = selected.value.map(a => a.id)
  if (!ids.length) return
  await accountApi.assignGroup({ account_ids: ids, group_id: batchGroupId.value ?? null })
  ElMessage.success(`已更新 ${ids.length} 个公众号的分组`)
  batchGroupId.value = null
  load()
}

// ---------- 导入 / 检索 ----------
async function doImport() {
  const lines = importText.value.split('\n').map(s => s.trim()).filter(Boolean)
  if (!lines.length) return ElMessage.warning('请输入至少一行')
  importing.value = true
  try {
    const resp = await accountApi.importAccounts({ lines, tags: importTags.value || undefined })
    importResult.value = resp.items || []
    ElMessage.success(`成功 ${resp.success} / 共 ${resp.total}`)
    // 导入成功后批量放入所选分组
    if (importGroupId.value) {
      await load()
      const names = importResult.value.filter(i => i.ok).map(i => i.name)
      const ids = accounts.value.filter(a => names.includes(a.name)).map(a => a.id)
      if (ids.length) await accountApi.assignGroup({ account_ids: ids, group_id: importGroupId.value })
    }
    load()
  } finally { importing.value = false }
}

function openSearch() { searchVisible.value = true; searchResults.value = []; searchQuery.value = '' }

async function doSearch() {
  if (!searchQuery.value.trim()) return ElMessage.warning('请输入关键词')
  searching.value = true
  try { searchResults.value = await accountApi.search({ query: searchQuery.value.trim() }) }
  finally { searching.value = false }
}

async function addOne(row) {
  await accountApi.add({ query: row.name })
  ElMessage.success(`已添加「${row.name}」`)
  load()
}

async function toggleMonitor(row, v) {
  await accountApi.update(row.id, { is_monitoring: v })
  row.is_monitoring = v
}

async function editTags(row) {
  const { value } = await ElMessageBox.prompt('输入标签（逗号分隔）', `标签 · ${row.name}`, {
    inputValue: row.tags || '', confirmButtonText: '保存', cancelButtonText: '取消',
  })
  if (value !== undefined) { await accountApi.update(row.id, { tags: value }); row.tags = value; ElMessage.success('已保存') }
}

async function remove(row) {
  await ElMessageBox.confirm(`删除「${row.name}」？其历史文章仍保留。`, '确认', { type: 'warning' })
  await accountApi.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.panel :deep(.el-card__body) { padding-top: 16px; }
.toolbar {
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 12px;
  padding-bottom: 16px; margin-bottom: 4px;
  border-bottom: 1px solid var(--ink-100);
}
.filters { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.actions { display: flex; align-items: center; gap: 8px; }
.count-hint { color: var(--ink-400); font-size: 12.5px; }

.batch-bar {
  display: flex; align-items: center; gap: 10px;
  background: var(--brand-50);
  border: 1px solid var(--brand-100);
  border-radius: 10px;
  padding: 8px 14px;
  margin: 12px 0;
}
.sel-info { color: var(--brand-600); font-size: 13px; }
.sel-info b { font-weight: 700; }

.acc-cell { display: flex; align-items: center; gap: 10px; }
.acc-name { display: flex; align-items: center; gap: 6px; font-weight: 600; color: var(--ink-900); }
.acc-sub { color: var(--ink-400); font-size: 12px; }
.tag { margin-right: 4px; }
</style>
