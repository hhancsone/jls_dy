const pool = require('../config/database.cjs')
const { extractVideoId } = require('../utils/helpers.cjs')
const { spawn } = require('child_process')
const fs = require('fs')
const path = require('path')

const getVideos = async (req, res) => {
  try {
    let query = 'SELECT id, video_id, title, author_name, video_url, tags, comment_count, status, created_at, created_by FROM videos WHERE status = 1'
    const params = []
    const { search } = req.query

    if (req.user && req.user.role !== 'admin') {
      query += ' AND created_by = ?'
      params.push(req.user.username || '管理员')
    }

    if (search) {
      query += ' AND (title LIKE ? OR video_url LIKE ?)'
      params.push(`%${search}%`, `%${search}%`)
    }

    query += ' ORDER BY created_at DESC'

    const [videos] = await pool.query(query, params)
    
    res.json({ 
      success: true, 
      videos 
    })
  } catch (error) {
    console.error('获取视频列表错误:', error)
    res.status(500).json({ success: false, message: '服务器错误' })
  }
}

const getVideoById = async (req, res) => {
  try {
    const { id } = req.params

    const [videos] = await pool.query(
      'SELECT * FROM videos WHERE id = ?',
      [id]
    )

    if (videos.length === 0) {
      return res.status(404).json({ success: false, message: '视频不存在' })
    }

    const video = videos[0]

    if (req.user && req.user.role !== 'admin' && video.created_by !== req.user.username) {
      return res.status(403).json({ success: false, message: '无权访问该视频' })
    }

    res.json({ 
      success: true, 
      video: videos[0]
    })
  } catch (error) {
    console.error('获取视频详情错误:', error)
    res.status(500).json({ success: false, message: '服务器错误' })
  }
}

const createVideo = async (req, res) => {
  try {
    const { url, title } = req.body

    if (!url) {
      return res.status(400).json({ success: false, message: '视频链接不能为空' })
    }

    const createdBy = req.user?.username || '管理员'

    const [result] = await pool.query(
      'INSERT INTO videos (video_id, video_url, title, tags, comment_count, status, created_by) VALUES (?, ?, ?, ?, ?, ?, ?)',
      [extractVideoId(url), url, title || '', '', 0, 1, createdBy]
    )

    res.json({ 
      success: true, 
      message: '添加视频成功',
      videoId: result.insertId
    })
  } catch (error) {
    console.error('添加视频错误:', error)
    res.status(500).json({ success: false, message: '服务器错误' })
  }
}

const deleteVideo = async (req, res) => {
  try {
    const { id } = req.params

    const [existingVideos] = await pool.query(
      'SELECT id, title, created_by FROM videos WHERE id = ?',
      [id]
    )

    if (existingVideos.length === 0) {
      return res.status(404).json({ success: false, message: '视频不存在' })
    }

    const video = existingVideos[0]

    if (req.user && req.user.role !== 'admin' && video.created_by !== req.user.username) {
      return res.status(403).json({ success: false, message: '无权删除该视频' })
    }
    
    const safeTitle = video.title ? video.title.replace(/[^\w\s\u4e00-\u9fa5-]/g, '') : 'video'
    const csvFileName = `${safeTitle}.csv`
    const csvFilePath = path.join(__dirname, '../services/data', csvFileName)

    if (fs.existsSync(csvFilePath)) {
      fs.unlinkSync(csvFilePath)
    }

    await pool.query('DELETE FROM videos WHERE id = ?', [id])

    res.json({ 
      success: true, 
      message: '删除视频成功'
    })
  } catch (error) {
    console.error('删除视频错误:', error)
    res.status(500).json({ success: false, message: '服务器错误' })
  }
}

const downloadCsv = async (req, res) => {
  try {
    const { id } = req.params

    const [videos] = await pool.query(
      'SELECT id, title, video_id FROM videos WHERE id = ?',
      [id]
    )

    if (videos.length === 0) {
      return res.status(404).json({ success: false, message: '视频不存在' })
    }

    const video = videos[0]
    
    const safeTitle = video.title ? video.title.replace(/[^\w\s\u4e00-\u9fa5-]/g, '') : 'video'
    const csvFileName = `${safeTitle}.csv`
    const csvFilePath = path.join(__dirname, '../services/data', csvFileName)

    if (!fs.existsSync(csvFilePath)) {
      return res.status(404).json({ success: false, message: 'CSV文件不存在' })
    }

    const fileContent = fs.readFileSync(csvFilePath)
    const bom = Buffer.from([0xEF, 0xBB, 0xBF])
    const contentWithBom = Buffer.concat([bom, fileContent])

    res.setHeader('Content-Type', 'text/csv; charset=utf-8')
    res.setHeader('Content-Disposition', `attachment; filename="${encodeURIComponent(csvFileName)}"`)
    res.send(contentWithBom)
  } catch (error) {
    console.error('下载CSV错误:', error)
    if (!res.headersSent) {
      res.status(500).json({ success: false, message: '服务器错误' })
    }
  }
}

module.exports = {
  getVideos,
  getVideoById,
  createVideo,
  deleteVideo,
  downloadCsv
}