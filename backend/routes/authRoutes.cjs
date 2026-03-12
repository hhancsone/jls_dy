const express = require('express')
const router = express.Router()
const authController = require('../controllers/authController.cjs')
const { authMiddleware } = require('../middleware/auth.cjs')

router.post('/login', authController.login)
router.post('/register', authController.register)
router.get('/user/:id', authController.getUserById)
router.post('/change-password', authMiddleware, authController.changePassword)

module.exports = router