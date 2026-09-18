<template>
  <div v-loading="loading">
    <el-card shadow="never" class="panel" v-if="article">
      <template #header>
        <div class="head">
          <div class="head-main">
            <el-button :icon="Back" circle size="small" class="back-btn" @click="$router.back()" />
            <div>
              <div class="title">{{ article.title }}
                <el-tag v-if="article.status !== 'normal'" size="small" type="danger">{{ article.status === 'deleted' ? '已删除' : '待确认' }}</el-tag>
              </div>
              <div class="sub">{{ article.account_name }} · {{ article.author }} · {{ fmtTime(article.publish_time) }}
                <el-link v-if="article.url" type="primary" :href="article.url" target="_blank" style="font-size:12px">原文链接</el-link>
              </div>
            </div>
          </div>
          <el-button type="primary" :icon="MagicStick" @click="$router.push({ path: '/analysis', query: { article_id: article.id } })">去分析</el-button>
        </div>
      </template>

      <!-- 最新指标 -->
      <div class="metric-grid" v-if="article.latest_metrics">
        <div v-for="m in metricCards" :key="m.label" class="metric-box">
          <div class="m-num">{{ fmtNum(m.value) }}</div>
          <div class="m-label">{{ m.label }}</div>
        </div>
      </div>

      <el-tabs v-model="tab">
        <el-tab-pane label="正文" name="content">
          <div v-if="article.content_text" class="content-text">{{ article.content_text }}</div>
          <el-empty v-else description="未抓取正文（抓取时勾选「正文」字段）" :image-size="80" />
        </el-tab-pane>

        <el-tab-pane :label="`指标趋势(${metrics.length})`" name="metrics">
          <div ref="trendRef" style="height:320px" v-if="metrics.length"></div>
          <el-empty v-else description="暂无指标快照" :image-size="80" />
        </el-tab-pane>

        <el-tab-pane :label="`评论(${comments.length})`" name="comments">
          <template v-if="comments.length">
            <el-button size="small" style="margin-bottom:10px" @click="exportComments">导出评论</el-button>
            <el-table :data="comments" size="small" max-height="420">
              <el-table-column prop="nickname" label="昵称" width="140" show-overflow-tooltip />
              <el-table-column prop="content" label="内容" min-width="320" show-overflow-tooltip />
              <el-table-column prop="like_num" label="点赞" width="70" align="right" />
              <el-table-column label="类型" width="80" align="center">
                <template #default="{ row }">
                  <el-tag size="small" effect="plain" :type="row.is_sub ? 'info' : ''">{{ row.is_sub ? '回复' : '主评' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="comment_time" label="时间" width="150">
                <template #default="{ row }">{{ fmtTime(row.comment_time) }}</template>
              </el-table-column>
              <el-table-column label="状态" width="80" align="center">
                <template #default="{ row }">
                  <el-tag v-if="row.status !== 'normal'" size="small" type="warning">已隐藏</el-tag>
                  <span v-else class="sub">正常</span>
                </template>
              </el-table-column>
            </el-table>
          </template>
          <el-empty v-else :image-size="90">
            <template #description>
              <p v-if="article.latest_metrics?.comment_count > 0">
                指标显示本文约有 <b>{{ article.latest_metrics.comment_count }}</b> 条评论，但评论明细尚未入库。<br />
                请在「内容抓取」勾选「评论内容」后重新抓取。
              </p>
              <p v-else>暂无评论明细。若抓取时已勾选「评论内容」，则该文可能未开通评论或当前无评论。</p>
            </template>
          </el-empty>
        </el-tab-pane>

        <el-tab-pane :label="`分析结果(${results.length})`" name="analysis">
          <div v-for="r in results" :key="r.id" class="result-block">
            <div class="result-head">
              <el-tag size="small" :type="r.status === 'success' ? 'success' : r.status === 'failed' ? 'danger' : 'info'">{{ r.status }}</el-tag>
              <span class="sub">{{ r.model }} · {{ fmtTime(r.created_at) }} · {{ r.tokens }} tokens</span>
            </div>
            <pre class="result-text">{{ r.result_text || r.error }}</pre>
          </div>
          <el-empty v-if="!results.length" description="暂无分析结果" :image-size="80" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { Back, MagicStick } from '@element-plus/icons-vue'
import { articleApi, analysisApi, exportApi } from '../api'
import { downloadBlob } from '../utils/download'

const route = useRoute()
const id = route.params.id
const article = ref(null)
const metrics = ref([])
const comments = ref([])
const results = ref([])
const loading = ref(false)
const tab = ref('content')
const trendRef = ref(null)

function fmtTime(t) { return t ? new Date(t).toLocaleString() : '' }
function fmtNum(n) {
  if (n == null) return '—'
  return n >= 10000 ? (n / 10000).toFixed(1) + 'w' : n
}

const metricCards = computed(() => {
  const m = article.value?.latest_metrics || {}
  return [
    { label: '阅读', value: m.read_num }, { label: '点赞', value: m.like_num },
    { label: '在看', value: m.wow_num }, { label: '转发', value: m.share_num },
    { label: '收藏', value: m.collect_num }, { label: '评论', value: m.comment_count },
  ]
})

function drawTrend() {
  if (!trendRef.value || !metrics.value.length) return
  const chart = echarts.init(trendRef.value)
  const xs = metrics.value.map(m => new Date(m.fetched_at).toLocaleString())
  chart.setOption({
    color: ['#c7000b', '#2f6fed', '#7a4fd0'],
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(19,26,38,.92)', borderWidth: 0,
      textStyle: { color: '#fff', fontSize: 12 }, padding: [8, 12],
    },
    legend: { data: ['阅读', '点赞', '评论'], textStyle: { color: '#5b6472' }, top: 4 },
    grid: { left: 10, right: 20, top: 44, bottom: 10, containLabel: true },
    xAxis: {
      type: 'category', data: xs,
      axisLine: { lineStyle: { color: '#e4e8ef' } },
      axisLabel: { color: '#8a92a1', fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#eef1f6' } },
      axisLabel: { color: '#8a92a1', fontSize: 11 },
    },
    series: [
      { name: '阅读', type: 'line', smooth: true, symbolSize: 6, areaStyle: { opacity: .08 }, data: metrics.value.map(m => m.read_num) },
      { name: '点赞', type: 'line', smooth: true, symbolSize: 6, data: metrics.value.map(m => m.like_num) },
      { name: '评论', type: 'line', smooth: true, symbolSize: 6, data: metrics.value.map(m => m.comment_count) },
    ],
  })
  window.addEventListener('resize', () => chart.resize())
}

async function exportComments() {
  const blob = await exportApi.comments({ article_id: Number(id), fmt: 'xlsx' })
  downloadBlob(blob, `comments_${id}.xlsx`)
}

onMounted(async () => {
  loading.value = true
  try {
    article.value = await articleApi.detail(id)
    ;[metrics.value, comments.value, results.value] = await Promise.all([
      articleApi.metrics(id), articleApi.comments(id), analysisApi.results({ article_id: id }),
    ])
    setTimeout(drawTrend)
  } finally { loading.value = false }
})
</script>

<style scoped>
.head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.head-main { display: flex; align-items: flex-start; gap: 12px; min-width: 0; }
.back-btn { margin-top: 3px; flex-shrink: 0; }
.title { font-size: 17px; font-weight: 700; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; color: var(--ink-900); }
.sub { color: var(--ink-400); font-size: 13px; margin-top: 6px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }

.metric-grid {
  display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px;
  margin-bottom: 18px;
}
.metric-box {
  text-align: center;
  background: linear-gradient(180deg, #fafbfd 0%, #f4f6fa 100%);
  border: 1px solid var(--ink-100);
  border-radius: 12px;
  padding: 14px 0 12px;
  transition: all .2s ease;
}
.metric-box:hover { transform: translateY(-2px); box-shadow: var(--shadow-hover); }
.m-num { font-size: 21px; font-weight: 700; color: var(--ink-900); font-variant-numeric: tabular-nums; }
.m-label { color: var(--ink-400); font-size: 12px; margin-top: 3px; }

.content-text { white-space: pre-wrap; line-height: 1.9; color: var(--ink-700); font-size: 14.5px; }
.result-block {
  border: 1px solid var(--ink-100); border-radius: 12px;
  padding: 14px 16px; margin-bottom: 12px;
  background: #fff;
  transition: box-shadow .2s ease;
}
.result-block:hover { box-shadow: var(--shadow-card); }
.result-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.result-text { white-space: pre-wrap; word-break: break-word; margin: 0; font-family: inherit; line-height: 1.8; }
</style>
