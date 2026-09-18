<template>
  <div>
    <el-card shadow="never" class="panel">
      <template #header>
        <div class="card-headbar">
          <div class="panel-title">
            <span class="bar"></span>复核队列
            <span class="text-sub">文章被删除 / 评论异常，需人工决定保留原始数据或确认删除</span>
          </div>
          <el-radio-group v-model="status" size="small" @change="load">
            <el-radio-button value="pending">待处理</el-radio-button>
            <el-radio-button value="keep">已保留</el-radio-button>
            <el-radio-button value="deleted">已删除</el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <el-table :data="rows" v-loading="loading">
        <el-table-column label="类型" width="110">
          <template #default="{ row }">
            <el-tag size="small" :type="row.change_type === 'article_deleted' ? 'danger' : 'warning'">
              {{ typeText(row.change_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="文章" min-width="240">
          <template #default="{ row }">
            <el-link type="primary" @click="$router.push(`/articles/${row.article_id}`)">{{ row.article_title || `#${row.article_id}` }}</el-link>
          </template>
        </el-table-column>
        <el-table-column label="变更说明" min-width="220">
          <template #default="{ row }">
            <span class="note">{{ describe(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="检测时间" width="150">
          <template #default="{ row }">{{ fmtTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center" v-if="status === 'pending'">
          <template #default="{ row }">
            <el-button size="small" type="success" @click="resolve(row, 'keep')">保留原始</el-button>
            <el-button size="small" type="danger" @click="resolve(row, 'delete')">确认删除</el-button>
          </template>
        </el-table-column>
        <el-table-column prop="note" label="备注" min-width="140" v-else show-overflow-tooltip />
      </el-table>
      <el-empty v-if="!loading && !rows.length" description="没有待确认项" />
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { reviewApi } from '../api'

const rows = ref([])
const loading = ref(false)
const status = ref('pending')

function fmtTime(t) { return t ? new Date(t).toLocaleString() : '' }
function typeText(t) {
  return { article_deleted: '文章删除', comment_drop: '评论异常', comment_deleted: '评论删除' }[t] || t
}
function describe(row) {
  const o = row.old_data || {}, n = row.new_data || {}
  if (row.change_type === 'article_deleted') return `原文无法访问，原阅读 ${o.read_num ?? '—'}`
  if (row.change_type === 'comment_drop') return `评论数从 ${o.comment_count ?? '?'} 降至 ${n.comment_count ?? '?'}`
  return '检测到数据变更'
}

async function load() {
  loading.value = true
  try { rows.value = await reviewApi.list(status.value) }
  finally { loading.value = false }
}

async function resolve(row, action) {
  const tip = action === 'keep' ? '保留原始数据（忽略本次变更）' : '确认删除（软删，留痕）'
  const { value } = await ElMessageBox.prompt(`${tip}。可填写备注：`, typeText(row.change_type), {
    confirmButtonText: '确定', cancelButtonText: '取消', inputPlaceholder: '备注（可选）',
  })
  if (value === undefined) return
  await reviewApi.resolve(row.id, { action, note: value || undefined })
  ElMessage.success('已处理')
  load()
}

onMounted(load)
</script>

<style scoped>
.panel-title { display: flex; align-items: center; gap: 9px; font-weight: 600; }
.panel-title .bar { width: 4px; height: 16px; border-radius: 2px; background: linear-gradient(to bottom, #f0a63c, #e08a00); }
.note { color: var(--ink-700); font-size: 13px; }
</style>
