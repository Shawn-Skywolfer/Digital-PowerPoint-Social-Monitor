<template>
  <div>
    <el-card shadow="never" class="panel">
      <div class="toolbar">
        <div class="filters">
          <el-select v-model="query.account_ids" multiple collapse-tags filterable placeholder="公众号" style="width:210px" @change="load">
            <el-option v-for="a in accounts" :key="a.id" :label="a.name" :value="a.id" />
          </el-select>
          <el-input v-model="query.keyword" placeholder="标题关键词" clearable style="width:180px" :prefix-icon="SearchIcon" @keyup.enter="load" />
          <el-date-picker v-model="range" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" @change="load" />
          <el-select v-model="query.sort_by" style="width:130px" @change="load">
            <el-option label="按发布时间" value="publish_time" />
            <el-option label="按阅读量" value="read_num" />
            <el-option label="按点赞" value="like_num" />
            <el-option label="按评论数" value="comment_count" />
          </el-select>
          <el-button type="primary" :icon="SearchIcon" @click="load">查询</el-button>
        </div>
        <div class="actions">
          <el-button type="success" plain :icon="DownloadIcon" :disabled="!selection.length" @click="exportSelected">
            导出选中<template v-if="selection.length">（{{ selection.length }}）</template>
          </el-button>
          <el-button plain :icon="DownloadIcon" @click="exportAll">导出全部</el-button>
        </div>
      </div>

      <el-table :data="rows" v-loading="loading" @selection-change="s => selection = s">
        <el-table-column type="selection" width="46" />
        <el-table-column label="标题" min-width="300">
          <template #default="{ row }">
            <el-link type="primary" class="art-link" @click="$router.push(`/articles/${row.id}`)">{{ row.title }}</el-link>
            <div class="sub">{{ row.account_name }} · {{ fmtTime(row.publish_time) }}
              <el-tag v-if="row.status !== 'normal'" size="small" type="danger" effect="plain">{{ row.status === 'deleted' ? '已删除' : '待确认' }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="read_num" label="阅读" width="95" align="right" sortable>
          <template #default="{ row }"><span class="num">{{ fmtNum(row.read_num) }}</span></template>
        </el-table-column>
        <el-table-column prop="like_num" label="点赞" width="85" align="right">
          <template #default="{ row }"><span class="num">{{ fmtNum(row.like_num) }}</span></template>
        </el-table-column>
        <el-table-column prop="wow_num" label="在看" width="85" align="right">
          <template #default="{ row }"><span class="num">{{ fmtNum(row.wow_num) }}</span></template>
        </el-table-column>
        <el-table-column prop="comment_count" label="评论" width="85" align="right">
          <template #default="{ row }"><span class="num">{{ fmtNum(row.comment_count) }}</span></template>
        </el-table-column>
        <el-table-column label="正文" width="70" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.content_fetched" color="#2fa35c"><CircleCheckFilled /></el-icon>
            <span v-else class="sub">—</span>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size"
        :total="total" :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper"
        style="margin-top:16px; justify-content:flex-end" @change="load" />
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { CircleCheckFilled, Search as SearchIcon, Download as DownloadIcon } from '@element-plus/icons-vue'
import { accountApi, articleApi, exportApi } from '../api'
import { downloadBlob, filenameFromHeaders } from '../utils/download'

const accounts = ref([])
const rows = ref([])
const total = ref(0)
const loading = ref(false)
const selection = ref([])
const range = ref(null)
const query = ref({ account_ids: [], keyword: '', sort_by: 'publish_time', page: 1, page_size: 20 })

function fmtTime(t) { return t ? new Date(t).toLocaleDateString() : '' }
function fmtNum(n) {
  if (n == null) return '—'
  return n >= 10000 ? (n / 10000).toFixed(1) + 'w' : n
}

function buildParams() {
  const q = query.value
  return {
    account_ids: q.account_ids.length ? q.account_ids.join(',') : undefined,
    keyword: q.keyword || undefined,
    sort_by: q.sort_by, sort_desc: true, page: q.page, page_size: q.page_size,
    time_start: range.value?.[0] ? range.value[0].toISOString() : undefined,
    time_end: range.value?.[1] ? range.value[1].toISOString() : undefined,
  }
}

async function load() {
  loading.value = true
  try {
    const resp = await articleApi.list(buildParams())
    rows.value = resp.items; total.value = resp.total
  } finally { loading.value = false }
}

async function doExport(params) {
  const blob = await exportApi.articles({ ...params, fmt: 'xlsx' })
  downloadBlob(blob, filenameFromHeaders(blob.headers || {}, `articles_${Date.now()}.xlsx`))
}
function exportSelected() { doExport({ ids: selection.value.map(r => r.id).join(',') }) }
function exportAll() { doExport({ account_ids: query.value.account_ids.join(',') || undefined, keyword: query.value.keyword || undefined }) }

onMounted(async () => {
  accounts.value = await accountApi.list()
  load()
})
</script>

<style scoped>
.panel :deep(.el-card__body) { padding-top: 16px; }
.toolbar {
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 12px;
  padding-bottom: 16px; margin-bottom: 4px;
  border-bottom: 1px solid var(--ink-100);
}
.filters { display: flex; gap: 10px; flex-wrap: wrap; }
.actions { display: flex; gap: 8px; }
.sub { color: var(--ink-400); font-size: 12px; margin-top: 3px; }
.art-link { font-weight: 500; font-size: 13.5px; }
</style>
