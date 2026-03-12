const pool = require('../config/database.cjs')

const authMiddleware = async (req, res, next) => {
  const userId = req.headers['x-user-id']
  
  if (!userId) {
    return res.status(401).json({ success: false, message: '未登录' })
  }
  
  try {
    const [users] = await pool.query(
      'SELECT id, username, email, role, avatar FROM users WHERE id = ?',
      [userId]
    )
    
    if (users.length === 0) {
      return res.status(401).json({ success: false, message: '用户不存在' })
    }
    
    req.user = users[0]
    next()
  } catch (error) {
    console.error('认证中间件错误:', error)
    res.status(500).json({ success: false, message: '服务器错误' })
  }
}

const adminMiddleware = (req, res, next) => {
  if (!req.user || req.user.role !== 'admin') {
    return res.status(403).json({ success: false, message: '权限不足' })
  }
  next()
}

module.exports = {
  authMiddleware,
  adminMiddleware
}