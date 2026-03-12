const express = require('express')
const router = express.Router()
const userController = require('../controllers/userController.cjs')

router.get('/', userController.getUsers)
router.post('/', userController.createUser)
router.post('/batch', userController.batchCreateUsers)
router.put('/:id', userController.updateUser)
router.delete('/:id', userController.deleteUser)

module.exports = router