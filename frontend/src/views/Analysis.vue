<template>
  <div>
    <el-row :gutter="16">
      <!-- 分析模块与维度设置 -->
      <el-col :span="9">
        <el-card shadow="never" class="panel">
          <template #header>
            <div class="card-headbar"><div class="panel-title"><span class="bar"></span>分析框架</div>
              <div class="actions">
                <el-button size="small" @click="importVisible = true">导入框架</el-button>
                <el-button size="small" type="primary" @click="openModule()">新建框架</el-button>
              </div>
            </div>
          </template>
          <el-collapse v-model="activeModule" accordion>
            <el-collapse-item v-for="m in modules" :key="m.id" :name="m.id">
              <template #title>
                <div class="mod-title">
                  <span>{{ m.name }}</span>
                  <el-tag size="small" :type="m.target === 'collection' ? 'warning' : 'default'" effect="plain">
                    {{ { content: '正文', comment: '评论', both: '正文+评论', collection: '聚合' }[m.target] || m.target }}
                  </el-tag>
                  <el-tag v-if="m.builtin" size="small" type="info" effect="plain">内置</el-tag>
                </div>
              </template>
              <div class="dim-list">
                <div v-for="d in m.dimensions" :key="d.id" class="dim-item">
                  <el-checkbox :model-value="d.enabled" @change="v => toggleDim(d, v)">{{ d.name }}</el-checkbox>
                  <el-button link type="primary" size="small" @click="editDim(m, d)">编辑</el-button>
                  <el-button v-if="!m.builtin" link type="danger" size="small" @click="removeDim(d)">删</el-button>
                </div>
                <div class="dim-actions">
                  <el-button size="small" @click="addDim(m)">+ 维度</el-button>
                  <el-button size="small" @click="exportModule(m)">导出</el-button>
                  <el-button v-if="!m.builtin" size="small" type="danger" plain @click="removeModule(m)">删除模块</el-button>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </el-card>
      </el-col>

      <!-- 运行分析 -->
      <el-col :span="15">
        <el-card shadow="never" class="panel">
          <template #header>
            <div class="card-headbar">
              <div class="panel-title"><span class="bar"></span>运行分析</div>
              <span class="text-sub">选择内容 → 指定框架与模型 → 一键洞察</span>
            </div>
          </template>
          <el-form label-position="top">
            <el-form-item label="分析内容（三种方式可组合）">
              <div class="pick-actions">
                <el-button type="primary" plain :icon="Document" @click="openPicker">选择文章</el-button>
                <el-button plain :icon="Download" @click="openTaskImport">从抓取任务导入</el-button>
                <el-button plain :icon="EditPen" @click="customVisible = true">录入自定义内容</el-button>
              </div>
              <div v-if="picked.length || customItems.length" class="picked-box">
                <el-tag v-for="a in picked" :key="'a' + a.id" closable @close="unpick(a.id)">{{ a.title }}</el-tag>
                <el-tag v-for="(c, i) in customItems" :key="'c' + i" type="warning" closable
                  @close="customItems.splice(i, 1)">自定义：{{ c.title || '未命名' }}</el-tag>
              </div>
              <div v-else class="empty-hint">尚未选择内容。可从文章库多选、整任务导入，或直接粘贴文本。</div>
            </el-form-item>
            <el-form inline>
              <el-form-item label="分析模块">
                <el-select v-model="run.module_id" style="width:160px" @change="run.dimension_ids = []">
                  <el-option v-for="m in modules" :key="m.id" :label="m.name" :value="m.id" />
                </el-select>
              </el-form-item>
              <el-form-item label="模型">
                <el-select v-model="run.llm_config_id" style="width:180px">
                  <el-option v-for="l in llms" :key="l.id" :label="l.name" :value="l.id" />
                </el-select>
              </el-form-item>
              <el-form-item label="维度（默认全部启用）">
                <el-select v-model="run.dimension_ids" multiple style="width:220px" placeholder="全部启用维度">
                  <el-option v-for="d in currentDims" :key="d.id" :label="d.name" :value="d.id" />
                </el-select>
              </el-form-item>
              <el-form-item label=" ">
                <el-button :icon="Plus" @click="customDims.push({ name: '', prompt: '' })">临时维度</el-button>
              </el-form-item>
              <el-form-item label=" ">
                <el-button type="primary" :loading="running" @click="doRun">
                  {{ isCollectionModule ? '开始聚合分析' : '开始分析' }}{{ picked.length + customItems.length ? `（${picked.length + customItems.length} 项）` : '' }}
                </el-button>
              </el-form-item>
            </el-form>
            <!-- 临时自定义维度（Prompt 形式，仅本次运行） -->
            <div v-if="customDims.length" class="custom-dims">
              <div v-for="(d, i) in customDims" :key="i" class="custom-dim-row">
                <el-input v-model="d.name" placeholder="维度名，如：竞品动态" style="width:180px" />
                <el-input v-model="d.prompt" placeholder="维度提示词（Prompt），如：总结文中提到的竞品及其动作" style="flex:1" />
                <el-button link type="danger" @click="customDims.splice(i, 1)">移除</el-button>
              </div>
            </div>
            <el-alert v-if="isCollectionModule" type="warning" :closable="false" class="col-hint">
              聚合分析：把所选内容作为整体提炼议题，按议题汇总总阅读量/总点赞，输出一份综合报告（结果在下方「聚合报告」页签）。
            </el-alert>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <!-- ============ 分析任务中心：历史任务 + 结果内容 ============ -->
    <el-card shadow="never" class="panel tasks-panel">
      <template #header>
        <div class="card-headbar">
          <div class="panel-title">
            <span class="bar"></span>分析任务中心
            <span class="text-sub">共 {{ batches.length }} 次单篇分析 · {{ collections.length }} 份聚合报告</span>
          </div>
          <div class="actions">
            <el-button size="small" :icon="Refresh" circle @click="reloadAll" />
            <el-button size="small" @click="exportResults" :disabled="!results.length">导出全部</el-button>
          </div>
        </div>
      </template>

      <el-tabs v-model="resultTab">
        <!-- 单篇分析任务（按批次分组） -->
        <el-tab-pane label="单篇分析任务" name="single">
          <el-empty v-if="!batches.length" description="还没有分析任务，去上方发起一次分析吧" :image-size="90" />
          <div v-else class="batch-list">
            <div v-for="b in batches" :key="b.batch_id" class="batch-card" :class="{ open: openBatches.has(b.batch_id) }">
              <!-- 批次头 -->
              <div class="batch-head" @click="toggleBatch(b.batch_id)">
                <el-icon class="arrow" :class="{ open: openBatches.has(b.batch_id) }"><ArrowRight /></el-icon>
                <span class="batch-title">{{ b.module }}</span>
                <el-tag size="small" effect="plain">{{ b.model || '默认模型' }}</el-tag>
                <span class="batch-meta">{{ b.items.length }} 篇文章 · {{ fmtTime(b.time) }}</span>
                <span class="batch-status">
                  <el-tag v-if="b.ok" size="small" type="success" effect="plain">成功 {{ b.ok }}</el-tag>
                  <el-tag v-if="b.failed" size="small" type="danger" effect="plain">失败 {{ b.failed }}</el-tag>
                  <el-tag v-if="b.running" size="small" type="warning" effect="plain">
                    <el-icon class="is-loading"><Loading /></el-icon> 分析中 {{ b.running }}
                  </el-tag>
                  <el-button v-if="!b.batch_id.startsWith('legacy-')" size="small" link type="primary"
                    @click.stop="exportBatch(b)">导出</el-button>
                </span>
              </div>
              <!-- 批次内容：逐篇结果 -->
              <div v-show="openBatches.has(b.batch_id)" class="batch-body">
                <div v-for="r in b.items" :key="r.id" class="result-row">
                  <div class="result-row-head" @click="toggleResult(r.id)">
                    <el-icon class="arrow" :class="{ open: openResults.has(r.id) }"><ArrowRight /></el-icon>
                    <el-link type="primary" class="result-title" @click.stop="$router.push(`/articles/${r.article_id}`)">
                      {{ articleTitle(r.article_id) }}
                    </el-link>
                    <el-tag size="small" :type="statusTag(r.status)">{{ statusText(r.status) }}</el-tag>
                    <span class="result-meta">
                      <template v-if="r.tokens">{{ r.tokens }} tokens · </template>{{ fmtTime(r.created_at) }}
                    </span>
                  </div>
                  <div v-show="openResults.has(r.id)" class="result-content">
                    <pre v-if="r.result_text || r.error" class="result-text">{{ r.result_text || r.error }}</pre>
                    <div v-else class="result-pending">
                      <el-icon class="is-loading"><Loading /></el-icon> 分析进行中，稍候自动刷新…
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 聚合报告 -->
        <el-tab-pane label="聚合报告" name="collection">
          <el-empty v-if="!collections.length" description="暂无聚合报告" :image-size="90" />
          <div v-else class="collection-list">
            <div v-for="c in collections" :key="c.id" class="collection-card" @click="viewCollection(c)">
              <div class="col-head">
                <span class="col-title">聚合报告 #{{ c.id }}</span>
                <el-tag size="small" :type="statusTag(c.status)">{{ statusText(c.status) }}</el-tag>
              </div>
              <div class="col-sub">{{ moduleName(c.module_id) }} · {{ c.model }} · 覆盖 {{ c.article_total }} 篇 · {{ fmtTime(c.created_at) }}</div>
              <div v-if="c.result_json?.overview" class="col-overview">{{ c.result_json.overview }}</div>
              <div v-if="c.result_json?.topics?.length" class="col-topics">
                <el-tag v-for="t in c.result_json.topics.slice(0, 4)" :key="t.name" size="small" effect="plain">{{ t.name }}</el-tag>
                <span v-if="c.result_json.topics.length > 4" class="text-sub">等 {{ c.result_json.topics.length }} 个议题</span>
              </div>
              <div class="col-foot" @click.stop>
                <el-button link type="primary" @click="viewCollection(c)">查看详情</el-button>
                <el-button link type="primary" :disabled="c.status !== 'success'" @click="exportCollection(c)">导出</el-button>
                <el-button link type="danger" @click="removeCollection(c)">删除</el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 文章选择器 -->
    <el-dialog v-model="pickerVisible" title="选择文章（可多选，跨页保留）" width="920px">
      <div class="picker-filters">
        <el-select v-model="picker.group_id" placeholder="分组" clearable style="width:140px" @change="picker.account_ids = []; searchPicker()">
          <el-option v-for="g in groups" :key="g.id" :label="g.name" :value="g.id" />
        </el-select>
        <el-select v-model="picker.account_ids" multiple collapse-tags placeholder="公众号（可多选）" filterable style="width:220px" @change="searchPicker">
          <el-option v-for="a in pickerAccounts" :key="a.id" :label="a.name" :value="a.id" />
        </el-select>
        <el-input v-model="picker.keyword" placeholder="标题关键词" clearable style="width:170px" @keyup.enter="searchPicker" />
        <el-button type="primary" @click="searchPicker">查询</el-button>
      </div>
      <el-table ref="pickerTable" :data="pickerRows" row-key="id" size="small" max-height="380"
        v-loading="pickerLoading" @selection-change="onPickerSelect">
        <el-table-column type="selection" width="42" reserve-selection />
        <el-table-column prop="title" label="标题" min-width="280" show-overflow-tooltip />
        <el-table-column prop="account_name" label="公众号" width="130" show-overflow-tooltip />
        <el-table-column label="发布时间" width="150">
          <template #default="{ row }">{{ fmtTime(row.publish_time) }}</template>
        </el-table-column>
        <el-table-column prop="read_num" label="阅读" width="90" align="right" />
      </el-table>
      <div class="picker-foot">
        <el-pagination layout="total, prev, pager, next" :total="pickerTotal"
          :page-size="picker.page_size" :current-page="picker.page"
          @current-change="p => { picker.page = p; searchPicker() }" />
        <div>
          <span class="sel-count">本次已选 {{ picked.length }} 篇</span>
          <el-button @click="pickerVisible = false">完成</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 从抓取任务导入 -->
    <el-dialog v-model="taskVisible" title="从抓取任务导入全部文章" width="720px">
      <el-table :data="fetchTasks" size="small" max-height="400" v-loading="taskLoading">
        <el-table-column prop="id" label="任务ID" width="80" />
        <el-table-column label="发起时间" width="160">
          <template #default="{ row }">{{ fmtTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status === 'success' ? 'success' : 'info'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="文章数" width="90" align="center">
          <template #default="{ row }">{{ (row.article_ids || []).length }}</template>
        </el-table-column>
        <el-table-column label="说明" min-width="140">
          <template #default="{ row }">新增{{ row.new_articles }} 更新{{ row.updated_articles }}</template>
        </el-table-column>
        <el-table-column label="操作" width="90" align="center">
          <template #default="{ row }">
            <el-button size="small" type="primary" :disabled="!(row.article_ids || []).length" @click="importTask(row)">导入</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 录入自定义内容 -->
    <el-dialog v-model="customVisible" title="录入自定义内容" width="640px">
      <el-form label-position="top">
        <el-form-item label="标题（可选）">
          <el-input v-model="customForm.title" placeholder="给这段内容起个名字，便于识别" />
        </el-form-item>
        <el-form-item label="正文内容">
          <el-input v-model="customForm.content" type="textarea" :rows="10" placeholder="直接粘贴要分析的文本内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="customVisible = false">取消</el-button>
        <el-button type="primary" @click="addCustom">添加</el-button>
      </template>
    </el-dialog>

    <!-- 模块编辑 -->
    <el-dialog v-model="moduleVisible" :title="moduleForm.id ? '编辑框架' : '新建框架'" width="520px">
      <el-form label-position="top">
        <el-form-item label="框架名称"><el-input v-model="moduleForm.name" /></el-form-item>
        <el-form-item label="分析对象">
          <el-radio-group v-model="moduleForm.target">
            <el-radio value="content">正文</el-radio><el-radio value="comment">评论</el-radio>
            <el-radio value="collection">聚合（多文综合）</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="提示词模板（可用 {title} {content} {comments} {dimensions} {account}；聚合可用 {count} {article_list}）">
          <el-input v-model="moduleForm.prompt_template" type="textarea" :rows="6" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="moduleVisible = false">取消</el-button>
        <el-button type="primary" @click="saveModule">保存</el-button>
      </template>
    </el-dialog>

    <!-- 维度编辑 -->
    <el-dialog v-model="dimVisible" :title="dimForm.id ? '编辑维度' : '新增维度'" width="480px">
      <el-form label-position="top">
        <el-form-item label="维度名称"><el-input v-model="dimForm.name" /></el-form-item>
        <el-form-item label="维度提示词（可选，引导模型输出该维度）">
          <el-input v-model="dimForm.prompt" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dimVisible = false">取消</el-button>
        <el-button type="primary" @click="saveDim">保存</el-button>
      </template>
    </el-dialog>

    <!-- 导入维度 -->
    <el-dialog v-model="importVisible" title="导入分析维度 (JSON)" width="520px">
      <el-input v-model="importText" type="textarea" :rows="10"
        placeholder='{"module_name":"正文分析","target":"content","dimensions":[{"name":"核心观点","prompt":"..."}]}' />
      <template #footer>
        <el-button @click="importVisible = false">取消</el-button>
        <el-button type="primary" @click="doImportModule">导入</el-button>
      </template>
    </el-dialog>

    <!-- 聚合报告详情 -->
    <el-dialog v-model="collectionVisible" :title="`聚合报告 #${currentCollection?.id || ''}`" width="860px">
      <div v-if="currentCollection">
        <div class="sub">{{ currentCollection.model }} · {{ currentCollection.tokens }} tokens · 覆盖 {{ currentCollection.article_total }} 篇</div>
        <template v-if="currentCollection.status === 'success' && reportJson">
          <el-alert v-if="reportJson.overview" type="info" :closable="false" class="overview-box">
            <b>总体概述：</b>{{ reportJson.overview }}
          </el-alert>
          <h4 class="sec-title">议题排行（按关注度）</h4>
          <el-table :data="reportJson.topics || []" size="small">
            <el-table-column type="expand">
              <template #default="{ row }">
                <div class="topic-detail">
                  <p><b>议题要点：</b>{{ row.summary }}</p>
                  <p><b>代表文章：</b></p>
                  <div v-for="a in row.top_articles" :key="a.id" class="topic-article">
                    <el-link type="primary" @click="$router.push(`/articles/${a.id}`)">{{ a.title }}</el-link>
                    <span class="sub">阅读 {{ a.read_num ?? '—' }}</span>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column type="index" label="#" width="46" />
            <el-table-column prop="name" label="议题" min-width="160" show-overflow-tooltip />
            <el-table-column prop="article_count" label="篇数" width="70" align="center" />
            <el-table-column prop="total_read" label="总阅读" width="100" align="right" sortable />
            <el-table-column prop="total_like" label="总点赞" width="90" align="right" />
          </el-table>
          <template v-if="reportJson.dimension_insights && Object.keys(reportJson.dimension_insights).length">
            <h4 class="sec-title">维度洞察</h4>
            <div v-for="(v, k) in reportJson.dimension_insights" :key="k" class="dim-insight">
              <el-tag size="small" effect="plain">{{ k }}</el-tag>
              <span>{{ typeof v === 'string' ? v : JSON.stringify(v) }}</span>
            </div>
          </template>
        </template>
        <template v-else-if="currentCollection.status === 'failed'">
          <el-alert type="error" :closable="false" :title="currentCollection.error || '分析失败'" />
        </template>
        <template v-else>
          <el-alert type="info" :closable="false" title="分析进行中，请稍候刷新" />
        </template>
        <el-collapse style="margin-top:12px">
          <el-collapse-item title="查看 LLM 原始输出" name="raw">
            <pre class="result-text">{{ currentCollection.result_text }}</pre>
          </el-collapse-item>
        </el-collapse>
      </div>
      <template #footer>
        <el-button @click="collectionVisible = false">关闭</el-button>
        <el-button type="primary" :disabled="currentCollection?.status !== 'success'"
          @click="exportCollection(currentCollection)">导出报告</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Download, EditPen, Plus, Refresh } from '@element-plus/icons-vue'
import { analysisApi, articleApi, accountApi, fetchApi, llmApi, exportApi } from '../api'
import { downloadBlob } from '../utils/download'

const route = useRoute()
const modules = ref([])
const llms = ref([])
const activeModule = ref(null)
const run = ref({ module_id: null, llm_config_id: null, dimension_ids: [] })
const customDims = ref([])      // 临时维度 [{name, prompt}]（Prompt 形式，不存模块）
const running = ref(false)
const results = ref([])
const articleMap = ref({})
const resultTab = ref('single')
const collections = ref([])
const collectionVisible = ref(false)
const currentCollection = ref(null)

// ---- 任务中心展开状态 ----
const openBatches = ref(new Set())
const openResults = ref(new Set())
let pollTimer = null

// ---- 内容选择（文章 + 自定义）----
const picked = ref([])          // [{id, title}]
const customItems = ref([])     // [{title, content}]
const pickedIds = computed(() => new Set(picked.value.map(a => a.id)))

// 文章选择器
const pickerVisible = ref(false)
const pickerLoading = ref(false)
const pickerRows = ref([])
const pickerTotal = ref(0)
const pickerTable = ref(null)
const picker = ref({ group_id: null, account_ids: [], keyword: '', page: 1, page_size: 10 })
const accounts = ref([])
const groups = ref([])

// 任务导入
const taskVisible = ref(false)
const taskLoading = ref(false)
const fetchTasks = ref([])

// 自定义内容
const customVisible = ref(false)
const customForm = ref({ title: '', content: '' })

const moduleVisible = ref(false)
const moduleForm = ref({ id: null, name: '', target: 'content', prompt_template: '' })
const dimVisible = ref(false)
const dimForm = ref({ id: null, module_id: null, name: '', prompt: '' })
const importVisible = ref(false)
const importText = ref('')

const currentDims = computed(() => modules.value.find(m => m.id === run.value.module_id)?.dimensions || [])
const isCollectionModule = computed(() => modules.value.find(m => m.id === run.value.module_id)?.target === 'collection')
const reportJson = computed(() => currentCollection.value?.result_json || null)
const pickerAccounts = computed(() =>
  picker.value.group_id ? accounts.value.filter(a => a.group_id === picker.value.group_id) : accounts.value)

// ---- 按批次（一次「开始分析」= 一个批次）分组历史结果 ----
const batches = computed(() => {
  const map = new Map()
  for (const r of results.value) {
    const key = r.batch_id || `legacy-${r.id}`
    if (!map.has(key)) map.set(key, [])
    map.get(key).push(r)
  }
  return [...map.entries()].map(([batch_id, items]) => ({
    batch_id,
    items,
    module: moduleName(items[0].module_id),
    model: items[0].model,
    time: items[0].created_at,   // results 按 id 倒序，第一个即最新
    ok: items.filter(i => i.status === 'success').length,
    failed: items.filter(i => i.status === 'failed').length,
    running: items.filter(i => i.status === 'pending' || i.status === 'running').length,
  }))
})

function articleTitle(id) { return articleMap.value[id] || `#${id}` }
function moduleName(id) { return modules.value.find(m => m.id === id)?.name || `#${id}` }
function fmtTime(t) { return t ? new Date(t).toLocaleString() : '' }
function statusTag(s) { return { success: 'success', failed: 'danger', running: 'warning', pending: 'info' }[s] || 'info' }
function statusText(s) { return { success: '成功', failed: '失败', running: '分析中', pending: '排队中' }[s] || s }

function toggleBatch(id) {
  const s = new Set(openBatches.value)
  s.has(id) ? s.delete(id) : s.add(id)
  openBatches.value = s
}
function toggleResult(id) {
  const s = new Set(openResults.value)
  s.has(id) ? s.delete(id) : s.add(id)
  openResults.value = s
}

async function loadModules() { modules.value = await analysisApi.modules() }
async function loadResults() {
  try {
    results.value = await analysisApi.results({ limit: 500 })
    // 补齐未知文章标题（如任务导入的文章）
    const missing = [...new Set(results.value.map(r => r.article_id))].filter(id => !articleMap.value[id])
    if (missing.length) {
      const resp = await articleApi.list({ ids: missing.join(',') })
      resp.items.forEach(i => (articleMap.value[i.id] = i.title))
    }
  } catch (e) { /* 拦截器已提示 */ }
}

function reloadAll() { loadResults(); loadCollections() }

// ---- 文章选择器逻辑 ----
function openPicker() {
  pickerVisible.value = true
  if (!pickerRows.value.length) searchPicker()
  else nextTick(restorePickerSelection)
}

async function searchPicker() {
  pickerLoading.value = true
  try {
    const resp = await articleApi.list({
      account_ids: picker.value.account_ids.length ? picker.value.account_ids.join(',') : undefined,
      keyword: picker.value.keyword || undefined,
      page: picker.value.page, page_size: picker.value.page_size, sort_by: 'publish_time',
    })
    pickerRows.value = resp.items
    pickerTotal.value = resp.total
    resp.items.forEach(i => (articleMap.value[i.id] = i.title))
    nextTick(restorePickerSelection)
  } finally { pickerLoading.value = false }
}

function restorePickerSelection() {
  if (!pickerTable.value) return
  pickerRows.value.forEach(r => {
    pickerTable.value.toggleRowSelection(r, pickedIds.value.has(r.id))
  })
}

function onPickerSelect(selectedRows) {
  // 同步当前页的勾选状态到 picked
  const pageIds = new Set(pickerRows.value.map(r => r.id))
  const selIds = new Set(selectedRows.map(r => r.id))
  picked.value = picked.value.filter(a => !pageIds.has(a.id))  // 先移除本页旧状态
  pickerRows.value.forEach(r => {
    if (selIds.has(r.id)) picked.value.push({ id: r.id, title: r.title })
  })
}

function unpick(id) {
  picked.value = picked.value.filter(a => a.id !== id)
  if (pickerVisible.value) restorePickerSelection()
}

// ---- 任务导入 ----
async function openTaskImport() {
  taskVisible.value = true
  taskLoading.value = true
  try { fetchTasks.value = await fetchApi.tasks(50) }
  finally { taskLoading.value = false }
}

async function importTask(row) {
  const resp = await fetchApi.taskArticles(row.id)
  const ids = resp.article_ids || []
  if (!ids.length) return ElMessage.warning('该任务没有可导入的文章')
  const arts = await articleApi.list({ ids: ids.join(',') })
  arts.items.forEach(i => (articleMap.value[i.id] = i.title))
  const exist = pickedIds.value
  let added = 0
  arts.items.forEach(i => {
    if (!exist.has(i.id)) { picked.value.push({ id: i.id, title: i.title }); added++ }
  })
  ElMessage.success(`已从任务 #${row.id} 导入 ${added} 篇（共 ${ids.length} 篇，去重后新增 ${added}）`)
  taskVisible.value = false
}

// ---- 自定义内容 ----
function addCustom() {
  if (!customForm.value.content.trim()) return ElMessage.warning('请填写正文内容')
  customItems.value.push({ title: customForm.value.title.trim(), content: customForm.value.content })
  customForm.value = { title: '', content: '' }
  customVisible.value = false
  ElMessage.success('已添加自定义内容')
}

async function loadCollections() {
  try { collections.value = await analysisApi.collections(50) }
  catch (e) { /* 拦截器已提示 */ }
}
async function viewCollection(row) {
  currentCollection.value = await analysisApi.collection(row.id)
  collectionVisible.value = true
}
async function removeCollection(row) {
  await ElMessageBox.confirm(`删除聚合报告 #${row.id}？`, '确认', { type: 'warning' })
  await analysisApi.removeCollection(row.id)
  ElMessage.success('已删除')
  loadCollections()
}

async function doRun() {
  if (!picked.value.length && !customItems.value.length) return ElMessage.warning('请选择文章或录入自定义内容')
  if (!run.value.module_id) return ElMessage.warning('请选择分析框架')
  if (!run.value.llm_config_id) return ElMessage.warning('请选择模型')
  const extraDims = customDims.value.filter(d => d.name.trim())
  running.value = true
  try {
    const resp = await analysisApi.run({
      article_ids: picked.value.map(a => a.id),
      module_id: run.value.module_id,
      llm_config_id: run.value.llm_config_id,
      dimension_ids: run.value.dimension_ids.length ? run.value.dimension_ids : undefined,
      custom_items: customItems.value.length ? customItems.value : undefined,
      custom_dimensions: extraDims.length ? extraDims : undefined,
    })
    if (resp.mode === 'collection') {
      ElMessage.success('聚合分析已提交，请在下方「聚合报告」页签查看')
      resultTab.value = 'collection'
      const poll = setInterval(async () => {
        await loadCollections()
        const rep = collections.value.find(c => c.batch_id === resp.batch_id)
        if (rep && (rep.status === 'success' || rep.status === 'failed')) clearInterval(poll)
      }, 3000)
      setTimeout(() => clearInterval(poll), 120000)
    } else {
      ElMessage.success('已提交，后台分析中，结果将在下方任务中心实时更新')
      if (resp.batch_id) openBatches.value = new Set([...openBatches.value, resp.batch_id])
      setTimeout(loadResults, 1500)
    }
  } finally { running.value = false }
}

// ---- 模块 ----
function openModule(m) {
  moduleForm.value = m ? { id: m.id, name: m.name, target: m.target, prompt_template: m.prompt_template } : { id: null, name: '', target: 'content', prompt_template: '' }
  moduleVisible.value = true
}
async function saveModule() {
  const f = moduleForm.value
  if (!f.name) return ElMessage.warning('请输入模块名')
  if (f.id) await analysisApi.updateModule(f.id, { name: f.name, target: f.target, prompt_template: f.prompt_template })
  else await analysisApi.createModule({ name: f.name, target: f.target, prompt_template: f.prompt_template })
  ElMessage.success('已保存'); moduleVisible.value = false; loadModules()
}
async function removeModule(m) {
  await ElMessageBox.confirm(`删除模块「${m.name}」及其维度？`, '确认', { type: 'warning' })
  await analysisApi.removeModule(m.id); ElMessage.success('已删除'); loadModules()
}

// ---- 维度 ----
function addDim(m) { dimForm.value = { id: null, module_id: m.id, name: '', prompt: '' }; dimVisible.value = true }
function editDim(m, d) { dimForm.value = { id: d.id, module_id: m.id, name: d.name, prompt: d.prompt }; dimVisible.value = true }
async function saveDim() {
  const f = dimForm.value
  if (!f.name) return ElMessage.warning('请输入维度名')
  if (f.id) await analysisApi.updateDimension(f.id, { name: f.name, prompt: f.prompt })
  else await analysisApi.addDimension(f.module_id, { name: f.name, prompt: f.prompt })
  ElMessage.success('已保存'); dimVisible.value = false; loadModules()
}
async function toggleDim(d, v) { await analysisApi.updateDimension(d.id, { enabled: v }); loadModules() }
async function removeDim(d) {
  await ElMessageBox.confirm(`删除维度「${d.name}」？`, '确认', { type: 'warning' })
  await analysisApi.removeDimension(d.id); ElMessage.success('已删除'); loadModules()
}

// ---- 导入/导出 ----
async function exportModule(m) {
  const blob = await analysisApi.exportModule(m.id)
  downloadBlob(blob, `module_${m.name}.json`)
}
async function doImportModule() {
  try {
    const payload = JSON.parse(importText.value)
    await analysisApi.importModule(payload)
    ElMessage.success('导入成功'); importVisible.value = false; importText.value = ''; loadModules()
  } catch (e) { ElMessage.error('JSON 格式错误：' + e.message) }
}

async function exportResults() {
  const blob = await exportApi.analysis({ fmt: 'xlsx' })
  downloadBlob(blob, `analysis_${Date.now()}.xlsx`)
}

// 文件名用时间戳：20260915_2130
function fileTs(t) {
  const d = t ? new Date(t) : new Date()
  const p = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}_${p(d.getHours())}${p(d.getMinutes())}`
}

// 导出单次分析任务（按批次）
async function exportBatch(b) {
  const blob = await exportApi.analysis({ batch_id: b.batch_id, fmt: 'xlsx' })
  downloadBlob(blob, `分析结果_${b.module}_${fileTs(b.time)}.xlsx`)
  ElMessage.success('已导出该任务的分析结果')
}

// 导出单份聚合报告（多 Sheet：概览 / 议题排行 / 文章清单）
async function exportCollection(c) {
  if (!c) return
  const blob = await exportApi.collection(c.id, { fmt: 'xlsx' })
  downloadBlob(blob, `聚合报告_${c.id}_${fileTs(c.created_at)}.xlsx`)
  ElMessage.success('已导出聚合报告')
}

onMounted(async () => {
  [llms.value, accounts.value, groups.value] = await Promise.all([llmApi.list(), accountApi.list(), accountApi.groups()])
  await loadModules()
  await loadResults()
  await loadCollections()
  // 默认展开最新一批
  if (batches.value.length) openBatches.value = new Set([batches.value[0].batch_id])
  if (route.query.article_id) {
    const a = await articleApi.detail(route.query.article_id)
    articleMap.value[a.id] = a.title
    picked.value = [{ id: a.id, title: a.title }]
  }
  // 有进行中任务时轮询刷新任务中心
  pollTimer = setInterval(() => {
    if (results.value.some(r => r.status === 'pending' || r.status === 'running')) loadResults()
    if (collections.value.some(c => c.status === 'pending' || c.status === 'running')) loadCollections()
  }, 5000)
})
onUnmounted(() => clearInterval(pollTimer))
</script>

<style scoped>
.panel-title { display: flex; align-items: center; gap: 9px; font-weight: 600; }
.panel-title .bar { width: 4px; height: 16px; border-radius: 2px; background: linear-gradient(to bottom, #e5323c, #c7000b); }
.mod-title { display: flex; align-items: center; gap: 8px; }
.dim-list { padding-left: 6px; }
.dim-item {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 8px; border-radius: 8px;
  transition: background .15s ease;
}
.dim-item:hover { background: var(--ink-50); }
.dim-item .el-checkbox { flex: 1; }
.dim-actions { margin-top: 10px; display: flex; gap: 4px; }
.sub { color: var(--ink-400); font-size: 12px; }
.result-text { white-space: pre-wrap; word-break: break-word; margin: 0; font-family: inherit; line-height: 1.8; }
.pick-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.picked-box {
  display: flex; flex-wrap: wrap; gap: 6px;
  margin-top: 10px; padding: 10px;
  max-height: 120px; overflow: auto; width: 100%;
  background: var(--ink-50); border-radius: 10px;
}
.empty-hint {
  color: var(--ink-400); font-size: 12.5px; margin-top: 10px;
  padding: 14px; width: 100%;
  background: var(--ink-50); border-radius: 10px;
  border: 1px dashed var(--ink-200);
  text-align: center;
}
.picker-filters { display: flex; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }
.picker-foot { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
.sel-count { color: var(--brand-600); font-size: 13px; margin-right: 12px; }
.custom-dims { margin-top: 4px; }
.custom-dim-row { display: flex; gap: 8px; align-items: center; margin-bottom: 6px; }
.col-hint { margin-top: 8px; }
.overview-box { margin: 8px 0 4px; }
.sec-title { margin: 14px 0 8px; }
.topic-detail { padding: 4px 12px; }
.topic-article { display: flex; gap: 10px; align-items: center; padding: 2px 0; }
.dim-insight { display: flex; gap: 8px; align-items: flex-start; padding: 5px 0; }
.dim-insight .el-tag { flex-shrink: 0; margin-top: 2px; }

/* ============ 任务中心 ============ */
.tasks-panel { margin-top: 16px; }

.batch-list { display: flex; flex-direction: column; gap: 12px; }
.batch-card {
  border: 1px solid var(--ink-100);
  border-radius: 12px;
  overflow: hidden;
  transition: box-shadow .2s ease, border-color .2s ease;
}
.batch-card:hover { box-shadow: var(--shadow-card); }
.batch-card.open { border-color: var(--ink-200); }
.batch-head {
  display: flex; align-items: center; gap: 10px;
  padding: 13px 16px;
  cursor: pointer; user-select: none;
  background: #fafbfd;
  transition: background .15s ease;
}
.batch-head:hover { background: var(--ink-100); }
.arrow { color: var(--ink-400); transition: transform .18s ease; flex-shrink: 0; }
.arrow.open { transform: rotate(90deg); }
.batch-title { font-weight: 600; color: var(--ink-900); }
.batch-meta { color: var(--ink-400); font-size: 12.5px; }
.batch-status { margin-left: auto; display: flex; gap: 6px; align-items: center; }

.batch-body { border-top: 1px solid var(--ink-100); }
.result-row + .result-row { border-top: 1px dashed var(--ink-100); }
.result-row-head {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px 10px 34px;
  cursor: pointer;
  transition: background .15s ease;
}
.result-row-head:hover { background: var(--ink-50); }
.result-title { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 500; }
.result-meta { color: var(--ink-400); font-size: 12px; flex-shrink: 0; }
.result-content { padding: 4px 20px 16px 46px; }
.result-content .result-text {
  background: var(--ink-50);
  border: 1px solid var(--ink-100);
  border-radius: 10px;
  padding: 14px 16px;
  font-size: 13.5px;
  color: var(--ink-700);
  max-height: 420px;
  overflow-y: auto;
}
.result-pending {
  display: flex; align-items: center; gap: 8px;
  color: var(--ink-400); font-size: 13px; padding: 8px 0;
}

/* 聚合报告卡片 */
.collection-list {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 14px;
}
.collection-card {
  border: 1px solid var(--ink-100);
  border-radius: 12px;
  padding: 16px 18px;
  cursor: pointer;
  transition: all .2s ease;
  background: #fff;
}
.collection-card:hover { box-shadow: var(--shadow-hover); transform: translateY(-2px); border-color: var(--brand-100); }
.col-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.col-title { font-weight: 600; color: var(--ink-900); }
.col-sub { color: var(--ink-400); font-size: 12px; margin-top: 6px; }
.col-overview {
  margin-top: 10px; font-size: 13px; color: var(--ink-700); line-height: 1.7;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}
.col-topics { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.col-foot { margin-top: 10px; padding-top: 8px; border-top: 1px dashed var(--ink-100); display: flex; gap: 4px; }
</style>
