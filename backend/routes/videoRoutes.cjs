const express = require('express')
const router = express.Router()
const videoController = require('../controllers/videoController.cjs')
const { authMiddleware } = require('../middleware/auth.cjs')

router.get('/', authMiddleware, videoController.getVideos)
router.get('/:id', authMiddleware, videoController.getVideoById)
router.post('/', authMiddleware, videoController.createVideo)
router.delete('/:id', authMiddleware, videoController.deleteVideo)
router.get('/:id/download-csv', authMiddleware, videoController.downloadCsv)

module.exports = router