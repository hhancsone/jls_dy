const express = require('express')
const router = express.Router()
const crawlController = require('../controllers/crawlController.cjs')
const { authMiddleware } = require('../middleware/auth.cjs')

router.post('/crawl-comments', authMiddleware, crawlController.crawlComments)

module.exports = router