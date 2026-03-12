const pool = require('../config/database.cjs')

const login = async (req, res) => {
  try {
    const { username, password } = req.body

    if (!username || !password) {
      return res.status(400).json({ success: false, message: '用户名和密码不能为空' })
    }

    const [users] = await pool.query(
      'SELECT id, username, password, email, avatar, role, status FROM users WHERE username = ?',
      [username]
    )

    if (users.length === 0) {
      return res.status(401).json({ success: false, message: '用户名或密码错误' })
    }

    const user = users[0]

    if (user.status === 0) {
      return res.status(403).json({ success: false, message: '账户已被禁用' })
    }

    const bcrypt = require('bcryptjs')
    const isPasswordValid = await bcrypt.compare(password, user.password)

    if (!isPasswordValid) {
      return res.status(401).json({ success: false, message: '用户名或密码错误' })
    }

    const { password: _, ...userWithoutPassword } = user

    res.json({ 
      success: true, 
      message: '登录成功',
      user: userWithoutPassword
    })
  } catch (error) {
    console.error('登录错误:', error)
    res.status(500).json({ success: false, message: '服务器错误' })
  }
}

const register = async (req, res) => {
  try {
    const { username, email, password } = req.body

    if (!username || !password) {
      return res.status(400).json({ success: false, message: '用户名和密码不能为空' })
    }

    if (password.length < 6) {
      return res.status(400).json({ success: false, message: '密码长度至少为6位' })
    }

    const [existingUsers] = await pool.query(
      'SELECT id FROM users WHERE username = ?',
      [username]
    )

    if (existingUsers.length > 0) {
      return res.status(400).json({ success: false, message: '用户名已存在' })
    }

    const bcrypt = require('bcryptjs')
    const hashedPassword = await bcrypt.hash(password, 10)

    const [result] = await pool.query(
      'INSERT INTO users (username, password, email, role, status) VALUES (?, ?, ?, ?, ?)',
      [username, hashedPassword, email || null, 'user', 1]
    )

    res.json({ 
      success: true, 
      message: '注册成功',
      userId: result.insertId
    })
  } catch (error) {
    console.error('注册错误:', error)
    res.status(500).json({ success: false, message: '服务器错误' })
  }
}

const getUserById = async (req, res) => {
  try {
    const { id } = req.params

    const [users] = await pool.query(
      'SELECT id, username, email, avatar, role, status FROM users WHERE id = ?',
      [id]
    )

    if (users.length === 0) {
      return res.status(404).json({ success: false, message: '用户不存在' })
    }

    res.json({ 
      success: true, 
      user: users[0]
    })
  } catch (error) {
    console.error('获取用户信息错误:', error)
    res.status(500).json({ success: false, message: '服务器错误' })
  }
}

const changePassword = async (req, res) => {
  try {
    const { currentPassword, newPassword } = req.body
    const userId = req.user.id

    if (!currentPassword || !newPassword) {
      return res.status(400).json({ success: false, message: '当前密码和新密码不能为空' })
    }

    if (newPassword.length < 6) {
      return res.status(400).json({ success: false, message: '新密码长度至少为6位' })
    }

    const [users] = await pool.query(
      'SELECT password FROM users WHERE id = ?',
      [userId]
    )

    if (users.length === 0) {
      return res.status(404).json({ success: false, message: '用户不存在' })
    }

    const bcrypt = require('bcryptjs')
    const isPasswordValid = await bcrypt.compare(currentPassword, users[0].password)

    if (!isPasswordValid) {
      return res.status(401).json({ success: false, message: '当前密码错误' })
    }

    const hashedNewPassword = await bcrypt.hash(newPassword, 10)

    await pool.query(
      'UPDATE users SET password = ? WHERE id = ?',
      [hashedNewPassword, userId]
    )

    res.json({ 
      success: true, 
      message: '密码修改成功'
    })
  } catch (error) {
    console.error('修改密码错误:', error)
    res.status(500).json({ success: false, message: '服务器错误' })
  }
}

module.exports = {
  login,
  register,
  getUserById,
  changePassword
}