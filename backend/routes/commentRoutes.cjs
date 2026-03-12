const express = require('express')
const router = express.Router()
const { authMiddleware } = require('../middleware/auth.cjs')
const request = require('request')

router.get('/comments', authMiddleware, (req, res) => {
  try {
    const { video_id, sentiment, title, model } = req.query
    
    if (!video_id) {
      return res.status(400).json({
        success: false,
        message: '视频ID不能为空'
      })
    }

    const flaskUrl = 'http://localhost:5000/api/comments'
    
    const options = {
      url: flaskUrl,
      method: 'POST',
      json: true,
      body: {
        videoId: video_id,
        title: title || '',
        sentiment: sentiment || 'all',
        model: model || 'random_forest'
      }
    }

    request(options, (error, response, body) => {
      if (error) {
        console.error('请求Flask服务失败:', error)
        return res.status(500).json({
          success: false,
          message: '获取评论失败'
        })
      }

      res.status(response.statusCode).json(body)
    })
  } catch (error) {
    console.error('获取评论失败:', error)
    res.status(500).json({
      success: false,
      message: '获取评论失败'
    })
  }
})

module.exports = router
