const extractVideoId = (url) => {
  if (!url) return null
  
  const patterns = [
    /\/video\/(\d+)/,
    /v\.douyin\.com\/([a-zA-Z0-9_-]+)/,
    /douyin\.com\/video\/(\d+)/
  ]
  
  for (const pattern of patterns) {
    const match = url.match(pattern)
    if (match) return match[1]
  }
  
  return null
}

module.exports = {
  extractVideoId
}