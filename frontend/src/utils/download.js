// 触发浏览器下载 blob
export function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}

// 从 Content-Disposition 提取文件名，失败则用默认名
export function filenameFromHeaders(headers, fallback) {
  const cd = headers?.['content-disposition'] || ''
  const m = cd.match(/filename\*=UTF-8''([^;]+)/)
  return m ? decodeURIComponent(m[1]) : fallback
}
