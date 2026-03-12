const pool = require('../config/database.cjs')
const { extractVideoId } = require('../utils/helpers.cjs')

const crawlComments = async (req, res) => {
  try {
    const { videoUrl } = req.body

    if (!videoUrl) {
      return res.status(400).json({ success: false, message: '视频链接不能为空' })
    }

    const flaskPort = process.env.FLASK_PORT || 5000
    const flaskUrl = `http://localhost:${flaskPort}/api/crawl`

    const response = await fetch(flaskUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ videoUrl })
    })

    const data = await response.json()

    if (!data.success) {
      return res.status(500).json({ success: false, message: data.message || '爬取失败' })
    }

    const videoId = extractVideoId(videoUrl)
    const { title, tags, comment_count, author_name } = data.data

    const createdBy = req.user?.username || '管理员'

    const [existingVideos] = await pool.query(
      'SELECT id FROM videos WHERE video_id = ?',
      [videoId]
    )

    if (existingVideos.length > 0) {
      await pool.query(
        'UPDATE videos SET video_url = ?, title = ?, author_name = ?, tags = ?, comment_count = ?, status = ?, created_by = ? WHERE video_id = ?',
        [videoUrl, title || '', author_name || '', tags || '', comment_count || 0, 1, createdBy, videoId]
      )
    } else {
      await pool.query(
        'INSERT INTO videos (video_id, video_url, title, author_name, tags, comment_count, status, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        [videoId, videoUrl, title || '', author_name || '', tags || '', comment_count || 0, 1, createdBy]
      )
    }

    res.json({
      success: true,
      message: '爬取成功',
      comments: data.data.comments,
      videoInfo: {
        title,
        author_name,
        tags,
        comment_count
      }
    })
  } catch (error) {
    console.error('爬取评论错误:', error)
    res.status(500).json({ success: false, message: '服务器错误' })
  }
}

module.exports = {
  crawlComments
}