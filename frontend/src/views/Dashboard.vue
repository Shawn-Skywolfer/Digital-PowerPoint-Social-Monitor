<template>
  <div>
    <!-- 指标总览 -->
    <div class="stat-grid">
      <div v-for="c in cards" :key="c.label" class="stat-tile">
        <div class="icon-chip" :style="{ background: c.bg, color: c.color }">
          <el-icon :size="22"><component :is="c.icon" /></el-icon>
        </div>
        <div>
          <div class="stat-num">{{ c.value }}</div>
          <div class="stat-label">{{ c.label }}</div>
        </div>
      </div>
    </div>

    <el-row :gutter="18" style="margin-top:18px">
      <el-col :span="14">
        <el-card shadow="never" class="panel">
          <template #header>
            <div class="card-headbar">
              <div class="panel-title">
                <span class="bar"></span>近 7 天文章热度 Top 10
              </div>
              <el-radio-group v-model="metric" size="small" @change="loadTop">
                <el-radio-button value="read_num">阅读</el-radio-button>
                <el-radio-button value="like_num">点赞</el-radio-button>
                <el-radio-button value="wow_num">在看</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="chartRef" style="height:372px"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="never" class="panel review-panel">
          <template #header>
            <div class="card-headbar">
              <div class="panel-title"><span class="bar warn"></span>待确认事项</div>
              <el-link v-if="pendingReviews.length" type="primary" :underline="false" @click="$router.push('/reviews')">
                全部处理<el-icon><ArrowRight /></el-icon>
              </el-link>
            </div>
          </template>
          <el-empty v-if="!pendingReviews.length" description="暂无待确认，一切正常" :image-size="90" />
          <div v-else class="review-list">
            <div v-for="r in pendingReviews" :key="r.id" class="review-item" @click="$router.push('/reviews')">
              <span class="rv-dot" :class="r.change_type === 'article_deleted' ? 'danger' : 'warn'"></span>
              <div class="rv-main">
                <div class="rv-title">{{ r.article_title || ('文章#' + r.article_id) }}</div>
                <div class="rv-sub">{{ r.change_type === 'article_deleted' ? '原文疑似被删除' : '评论数据异常波动' }}</div>
              </div>
              <el-icon class="rv-arrow"><ArrowRight /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import * as echarts from 'echarts'
import { dashboardApi, reviewApi } from '../api'

const stats = ref({})
const pendingReviews = ref([])
const metric = ref('read_num')
const chartRef = ref(null)
let chart = null

const cards = computed(() => [
  { label: '监测公众号', value: stats.value.accounts_monitoring ?? 0, icon: 'OfficeBuilding', color: '#c7000b', bg: '#fdf1f2' },
  { label: '已抓取文章', value: stats.value.articles ?? 0, icon: 'Document', color: '#2f6fed', bg: '#eef4fe' },
  { label: '评论总数', value: stats.value.comments ?? 0, icon: 'ChatDotSquare', color: '#7a4fd0', bg: '#f4f0fc' },
  { label: '分析结果', value: stats.value.analysis_results ?? 0, icon: 'MagicStick', color: '#0e9aa7', bg: '#e8f7f8' },
  { label: '待确认', value: stats.value.pending_reviews ?? 0, icon: 'Warning', color: '#e08a00', bg: '#fdf3e3' },
  { label: '定时任务', value: stats.value.scheduled_jobs ?? 0, icon: 'AlarmClock', color: '#2fa35c', bg: '#ecf7f0' },
])

async function loadStats() {
  stats.value = await dashboardApi.stats()
  const r = await reviewApi.list('pending')
  pendingReviews.value = r.slice(0, 8)
}

async function loadTop() {
  const resp = await dashboardApi.topArticles({ metric: metric.value, days: 7, limit: 10 })
  const items = resp.items || []
  if (!chart) chart = echarts.init(chartRef.value)
  chart.setOption({
    grid: { left: 10, right: 44, top: 8, bottom: 8, containLabel: true },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(19,26,38,.92)',
      borderWidth: 0,
      textStyle: { color: '#fff', fontSize: 12 },
      padding: [8, 12],
    },
    xAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#eef1f6' } },
      axisLabel: { color: '#8a92a1', fontSize: 11 },
    },
    yAxis: {
      type: 'category', inverse: true,
      data: items.map(i => (i.title || '').slice(0, 16)),
      axisLabel: { width: 210, overflow: 'truncate', color: '#2b3444', fontSize: 12 },
      axisLine: { show: false }, axisTick: { show: false },
    },
    series: [{
      type: 'bar', barWidth: 14,
      itemStyle: {
        borderRadius: [0, 7, 7, 0],
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#e5323c' }, { offset: 1, color: '#f0817f' },
        ]),
      },
      label: {
        show: true, position: 'right',
        color: '#8a92a1', fontSize: 11,
        formatter: ({ value }) => value >= 10000 ? (value / 10000).toFixed(1) + 'w' : value,
      },
      data: items.map(i => i[metric.value] || 0),
    }],
  })
}

function onResize() { chart && chart.resize() }

onMounted(async () => {
  await loadStats()
  await loadTop()
  window.addEventListener('resize', onResize)
})
onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  chart && chart.dispose()
})
</script>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
}
@media (max-width: 1500px) { .stat-grid { grid-template-columns: repeat(3, 1fr); } }

.panel :deep(.el-card__body) { padding: 8px 12px 14px; }
.panel-title { display: flex; align-items: center; gap: 9px; font-weight: 600; }
.panel-title .bar { width: 4px; height: 16px; border-radius: 2px; background: linear-gradient(to bottom, #e5323c, #c7000b); }
.panel-title .bar.warn { background: linear-gradient(to bottom, #f0a63c, #e08a00); }

.review-panel :deep(.el-card__body) { padding: 12px 16px 16px; }
.review-list { display: flex; flex-direction: column; gap: 4px; max-height: 360px; overflow-y: auto; }
.review-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 12px; border-radius: 10px;
  cursor: pointer; transition: background .16s ease;
}
.review-item:hover { background: var(--ink-50); }
.review-item:hover .rv-arrow { opacity: 1; transform: translateX(0); }
.rv-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.rv-dot.danger { background: #d93026; box-shadow: 0 0 0 3px rgba(217, 48, 38, .14); }
.rv-dot.warn { background: #e08a00; box-shadow: 0 0 0 3px rgba(224, 138, 0, .14); }
.rv-main { flex: 1; min-width: 0; }
.rv-title { font-size: 13.5px; color: var(--ink-900); font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rv-sub { font-size: 12px; color: var(--ink-400); margin-top: 2px; }
.rv-arrow { color: var(--ink-300); opacity: 0; transform: translateX(-4px); transition: all .18s ease; }
</style>
