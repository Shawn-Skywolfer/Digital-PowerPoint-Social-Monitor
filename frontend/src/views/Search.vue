<template>
  <div>
    <!-- 检索条件 -->
    <el-card shadow="never" class="panel">
      <template #header>
        <div class="card-headbar">
          <div class="panel-title"><span class="bar"></span>关键词检索</div>
          <span class="text-sub">微信搜一搜 · 0.5 元/页 · 结果仅预览，选中后再入库</span>
        </div>
      </template>
      <el-form inline @submit.prevent>
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="如：数字能源、储能、超充" style="width:260px"
            clearable @keyup.enter="doSearch(true)" />
        </el-form-item>
        <el-form-item label="排序">
          <el-select v-model="query.sort_type" style="width:110px">
            <el-option label="综合" :value="0" />
            <el-option label="最新" :value="1" />
            <el-option label="最热" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="发布时间">
          <el-select v-model="query.publish_time_type" style="width:130px">
            <el-option label="不限" :value="0" />
            <el-option label="最近一天" :value="1" />
            <el-option label="最近七天" :value="2" />
            <el-option label="最近半年" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" :loading="searching" @click="doSearch(true)">搜索</el-button>
          <el-button :icon="RefreshLeft" :disabled="!searched" @click="reset">重置</el-button>
        </el-form-item>
      </el-form>
      <div v-if="searched" class="result-meta">
        <span>命中约 <b>{{ total ?? '—' }}</b> 条</span>
        <span class="sep">·</span>
        <span>已加载 <b>{{ items.length }}</b> 条</span>
        <template v-if="costInfo">
          <span class="sep">·</span>
          <span>累计扣费 <b>{{ costInfo.cost }}</b> 元，余额 <b>{{ costInfo.remain ?? '—' }}</b> 元</span>
        </template>
      </div>
    </el-card>

    <!-- 结果列表 -->
    <el-card v-if="searched" shadow="never" class="panel result-panel">
      <el-table ref="tableRef" :data="items" v-loading="searching" size="small"
        :row-key="row => row.url" @selection-change="onSelChange">
        <el-table-column type="selection" width="42" reserve-selection />
        <el-table-column label="标题 / 摘要" min-width="340">
          <template #default="{ row }">
            <a :href="row.url" target="_blank" rel="noopener" class="art-title">{{ row.title }}</a>
            <div v-if="row.digest" class="art-digest">{{ row.digest }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="account_name" label="公众号" width="150" show-overflow-tooltip />
        <el-table-column label="发布时间" width="150">
          <template #default="{ row }">{{ fmtTime(row.publish_time) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="96" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.in_library" size="small" type="success" class="lib-tag"
              @click="goArticle(row)">已在库中</el-tag>
            <el-tag v-else size="small" type="info">未入库</el-tag>
          </template>
        </el-table-column>
        <template #empty>暂无结果，换个关键词或放宽时间范围试试</template>
      </el-table>
      <div class="table-foot">
        <el-button v-if="continueFlag" :loading="loadingMore" @click="doSearch(false)">
          加载更多（0.5 元/页）
        </el-button>
        <span v-else-if="items.length" class="text-sub">已加载全部结果</span>
      </div>
    </el-card>

    <!-- 选中后的浮动操作条 -->
    <transition name="page">
      <div v-if="selected.length" class="action-bar">
        <span class="sel-text">已选 <b>{{ selected.length }}</b> 篇</span>
        <el-button size="small" @click="clearSel">清空</el-button>
        <el-button type="primary" size="small" :icon="Download" @click="dlVisible = true">批量下载</el-button>
        <el-button type="success" size="small" :icon="MagicStick" @click="openAnalyze">批量分析</el-button>
      </div>
    </transition>

    <!-- 批量下载 -->
    <el-dialog v-model="dlVisible" title="批量下载" width="500px">
      <el-alert type="info" :closable="false" class="dlg-alert">
        先把 {{ selected.length }} 篇文章建档入库，再按勾选字段逐篇抓取（后台任务，进度见「内容抓取」）。
      </el-alert>
      <el-form label-position="top">
        <el-form-item label="抓取字段">
          <el-checkbox-group v-model="dlFields">
            <el-checkbox value="content">正文（约 0.03 元/篇）</el-checkbox>
            <el-checkbox value="metrics">阅读/点赞等指标（约 0.06 元/篇）</el-checkbox>
            <el-checkbox value="comment">评论（约 0.06 元/篇）</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="预估费用">
          <span>约 <b class="cost">{{ estCost }}</b> 元（{{ selected.length }} 篇，已抓过正文的不会重复扣）</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlVisible = false">取消</el-button>
        <el-button type="primary" :loading="dlRunning" @click="doDownload">开始下载</el-button>
      </template>
    </el-dialog>

    <!-- 批量分析 -->
    <el-dialog v-model="anVisible" title="批量分析" width="560px">
      <el-alert type="info" :closable="false" class="dlg-alert">
        先把 {{ selected.length }} 篇文章建档入库（不含正文），再提交分析。
        若选「正文分析」类模块，建议先批量下载正文，否则只能基于标题/摘要分析。
      </el-alert>
      <el-form label-width="110px">
        <el-form-item label="分析模块">
          <el-select v-model="anForm.module_id" style="width:100%" placeholder="选择分析模块"
            @change="anForm.dimension_ids = []">
            <el-option v-for="m in modules" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型">
          <el-select v-model="anForm.llm_config_id" style="width:100%" placeholder="选择大模型配置">
            <el-option v-for="l in llms" :key="l.id" :label="l.name" :value="l.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="分析维度">
          <el-select v-model="anForm.dimension_ids" multiple style="width:100%" placeholder="默认全部启用">
            <el-option v-for="d in currentDims" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="anVisible = false">取消</el-button>
        <el-button type="primary" :loading="anRunning" @click="doAnalyze">提交分析</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Download, MagicStick, RefreshLeft, Search } from '@element-plus/icons-vue'
import { analysisApi, fetchApi, llmApi, searchApi } from '../api'

const router = useRouter()

// ---------- 检索 ----------
const query = reactive({ keyword: '', sort_type: 0, publish_time_type: 0 })
const searching = ref(false)
const loadingMore = ref(false)
const searched = ref(false)
const items = ref([])
const total = ref(null)
const continueFlag = ref(false)
const cursor = reactive({ offset: 0, cookies_buffer: '', current_page: 1 })
const costInfo = ref(null)          // { cost: 累计扣费, remain: 余额 }
const selected = ref([])
const tableRef = ref(null)

async function doSearch(isFirst) {
  const kw = query.keyword.trim()
  if (!kw) return ElMessage.warning('请输入关键词')
  if (isFirst) searching.value = true
  else loadingMore.value = true
  try {
    const resp = await searchApi.articles({
      keyword: kw,
      sort_type: query.sort_type,
      publish_time_type: query.publish_time_type,
      offset: isFirst ? 0 : cursor.offset,
      cookies_buffer: isFirst ? '' : cursor.cookies_buffer,
      current_page: isFirst ? 1 : cursor.current_page + 1,
    }, { timeout: 90000 })
    if (isFirst) {
      items.value = []
      total.value = null
      costInfo.value = null
      clearSel()
    }
    // 跨页按 url 去重合并（搜一搜翻页偶有重叠）
    const seen = new Set(items.value.map(i => i.url))
    for (const it of resp.items) {
      if (!seen.has(it.url)) { items.value.push(it); seen.add(it.url) }
    }
    total.value = resp.total ?? total.value
    continueFlag.value = resp.continue_flag
    cursor.offset = resp.offset
    cursor.cookies_buffer = resp.cookies_buffer
    cursor.current_page = resp.current_page
    if (resp.cost != null) {
      costInfo.value = {
        cost: ((costInfo.value?.cost || 0) + resp.cost).toFixed(2),
        remain: resp.remain,
      }
    }
    searched.value = true
  } finally {
    searching.value = false
    loadingMore.value = false
  }
}

function reset() {
  query.keyword = ''
  query.sort_type = 0
  query.publish_time_type = 0
  items.value = []
  selected.value = []
  searched.value = false
  continueFlag.value = false
  costInfo.value = null
}

function onSelChange(rows) { selected.value = rows }
function clearSel() { tableRef.value?.clearSelection(); selected.value = [] }
function fmtTime(t) { return t ? new Date(t).toLocaleString() : '' }
function goArticle(row) { if (row.article_id) router.push(`/articles/${row.article_id}`) }

// ---------- 入库（下载/分析共用第一步） ----------
async function importSelected() {
  const payload = selected.value.map(
    ({ url, title, account_name, digest, publish_time, cover }) =>
      ({ url, title, account_name, digest, publish_time, cover }))
  const resp = await searchApi.import(payload, { timeout: 120000 })
  // 返回的 article_ids 与提交顺序一致，回写在库标记
  resp.article_ids.forEach((id, i) => {
    const row = selected.value[i]
    if (row) { row.in_library = true; row.article_id = id }
  })
  if (resp.new_accounts > 0) {
    ElMessage.info(`已新建 ${resp.new_accounts} 个公众号档案（默认不监控，可在「公众号管理」开启）`)
  }
  return resp.article_ids
}

// ---------- 批量下载 ----------
const dlVisible = ref(false)
const dlRunning = ref(false)
const dlFields = ref(['content', 'metrics'])
const PRICE = { content: 0.03, metrics: 0.06, comment: 0.06 }
const estCost = computed(() =>
  (selected.value.length * dlFields.value.reduce((s, f) => s + (PRICE[f] || 0), 0)).toFixed(2))

async function doDownload() {
  if (!dlFields.value.length) return ElMessage.warning('请勾选要抓取的字段')
  dlRunning.value = true
  try {
    const ids = await importSelected()
    const fields = dlFields.value.flatMap(f =>
      f === 'metrics' ? ['read_num', 'like_num', 'wow_num', 'share_num', 'collect_num'] : [f])
    await fetchApi.createTask({ article_ids: ids, fields }, { timeout: 120000 })
    ElMessage.success('下载任务已创建，请在「内容抓取」查看进度')
    dlVisible.value = false
    router.push('/fetch')
  } finally { dlRunning.value = false }
}

// ---------- 批量分析 ----------
const anVisible = ref(false)
const anRunning = ref(false)
const modules = ref([])
const llms = ref([])
const anForm = reactive({ module_id: null, llm_config_id: null, dimension_ids: [] })
const currentDims = computed(() =>
  modules.value.find(m => m.id === anForm.module_id)?.dimensions || [])

async function openAnalyze() {
  anVisible.value = true
  if (!modules.value.length) {
    ;[modules.value, llms.value] = await Promise.all([analysisApi.modules(), llmApi.list()])
  }
}

async function doAnalyze() {
  if (!anForm.module_id) return ElMessage.warning('请选择分析模块')
  if (!anForm.llm_config_id) return ElMessage.warning('请选择模型')
  anRunning.value = true
  try {
    const ids = await importSelected()
    const resp = await analysisApi.run({
      article_ids: ids,
      module_id: anForm.module_id,
      llm_config_id: anForm.llm_config_id,
      dimension_ids: anForm.dimension_ids.length ? anForm.dimension_ids : undefined,
    }, { timeout: 120000 })
    ElMessage.success(resp.mode === 'collection' ? '聚合分析已提交' : '分析任务已提交')
    anVisible.value = false
    router.push('/analysis')
  } finally { anRunning.value = false }
}
</script>

<style scoped>
.panel-title { display: flex; align-items: center; gap: 9px; font-weight: 600; }
.panel-title .bar { width: 4px; height: 16px; border-radius: 2px; background: linear-gradient(to bottom, #e5323c, #c7000b); }
.card-headbar { display: flex; align-items: center; justify-content: space-between; }
.text-sub { color: var(--ink-400); font-size: 12px; }

.result-meta { color: var(--ink-500); font-size: 13px; display: flex; align-items: center; gap: 8px; }
.result-meta b { color: var(--ink-900); }
.result-meta .sep { color: var(--ink-300); }

.result-panel { margin-top: 16px; }
.art-title { color: var(--ink-900); font-weight: 600; text-decoration: none; line-height: 1.45; }
.art-title:hover { color: var(--brand-600, #c7000b); }
.art-digest {
  color: var(--ink-400); font-size: 12px; margin-top: 3px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.lib-tag { cursor: pointer; }
.table-foot { display: flex; justify-content: center; padding-top: 14px; }

.action-bar {
  position: fixed; bottom: 26px; left: 50%; transform: translateX(-50%);
  z-index: 30; display: flex; align-items: center; gap: 12px;
  background: #fff; border: 1px solid var(--ink-200); border-radius: 12px;
  padding: 10px 16px; box-shadow: 0 10px 32px rgba(15, 23, 42, .18);
}
.sel-text { font-size: 13px; color: var(--ink-500); }
.sel-text b { color: var(--ink-900); }

.dlg-alert { margin-bottom: 14px; }
.cost { color: #c7000b; }
</style>
