const pool = require('../config/database.cjs')
const bcrypt = require('bcryptjs')

const getUsers = async (req, res) => {
  try {
    const { search } = req.query
    
    let query = 'SELECT id, username, email, avatar, role, status, created_at FROM users'
    let params = []
    
    if (search) {
      query += ' WHERE username LIKE ? OR email LIKE ?'
      params = [`%${search}%`, `%${search}%`]
    }
    
    query += ' ORDER BY created_at DESC'
    
    const [users] = await pool.query(query, params)
    
    res.json({ 
      success: true, 
      users 
    })
  } catch (error) {
    console.error('获取用户列表错误:', error)
    res.status(500).json({ success: false, message: '服务器错误' })
  }
}

const createUser = async (req, res) => {
  try {
    const { username, email, password, role, status } = req.body

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
      return res.status(409).json({ success: false, message: '用户名已存在' })
    }

    const hashedPassword = await bcrypt.hash(password, 10)

    const [result] = await pool.query(
      'INSERT INTO users (username, password, email, role, status) VALUES (?, ?, ?, ?, ?)',
      [username, hashedPassword, email || null, role || 'user', status !== undefined ? status : 1]
    )

    const [newUser] = await pool.query(
      'SELECT id, username, email, avatar, role, status, created_at FROM users WHERE id = ?',
      [result.insertId]
    )

    res.json({ 
      success: true, 
      message: '添加用户成功',
      user: newUser[0]
    })
  } catch (error) {
    console.error('添加用户错误:', error)
    res.status(500).json({ success: false, message: '服务器错误' })
  }
}

const updateUser = async (req, res) => {
  try {
    const { id } = req.params
    const { username, email, password, role, status } = req.body

    const [existingUsers] = await pool.query(
      'SELECT id FROM users WHERE id = ?',
      [id]
    )

    if (existingUsers.length === 0) {
      return res.status(404).json({ success: false, message: '用户不存在' })
    }

    let updateFields = []
    let updateValues = []

    if (username) {
      updateFields.push('username = ?')
      updateValues.push(username)
    }
    if (email !== undefined) {
      updateFields.push('email = ?')
      updateValues.push(email || null)
    }
    if (password) {
      updateFields.push('password = ?')
      updateValues.push(await bcrypt.hash(password, 10))
    }
    if (role) {
      updateFields.push('role = ?')
      updateValues.push(role)
    }
    if (status !== undefined) {
      updateFields.push('status = ?')
      updateValues.push(status)
    }

    if (updateFields.length === 0) {
      return res.status(400).json({ success: false, message: '没有要更新的字段' })
    }

    updateValues.push(id)

    await pool.query(
      `UPDATE users SET ${updateFields.join(', ')} WHERE id = ?`,
      updateValues
    )

    const [updatedUser] = await pool.query(
      'SELECT id, username, email, avatar, role, status, created_at FROM users WHERE id = ?',
      [id]
    )

    res.json({ 
      success: true, 
      message: '更新用户成功',
      user: updatedUser[0]
    })
  } catch (error) {
    console.error('更新用户错误:', error)
    res.status(500).json({ success: false, message: '服务器错误' })
  }
}

const deleteUser = async (req, res) => {
  try {
    const { id } = req.params

    const [existingUsers] = await pool.query(
      'SELECT id FROM users WHERE id = ?',
      [id]
    )

    if (existingUsers.length === 0) {
      return res.status(404).json({ success: false, message: '用户不存在' })
    }

    await pool.query('DELETE FROM users WHERE id = ?', [id])

    res.json({ 
      success: true, 
      message: '删除用户成功'
    })
  } catch (error) {
    console.error('删除用户错误:', error)
    res.status(500).json({ success: false, message: '服务器错误' })
  }
}

const batchCreateUsers = async (req, res) => {
  try {
    const { users } = req.body

    if (!users || !Array.isArray(users) || users.length === 0) {
      return res.status(400).json({ success: false, message: '用户数据不能为空' })
    }

    const results = {
      success: 0,
      failed: 0,
      errors: []
    }

    for (const userData of users) {
      try {
        const { username, email, password, role, status } = userData

        if (!username || !password) {
          results.failed++
          results.errors.push({ username, message: '用户名和密码不能为空' })
          continue
        }

        if (password.length < 6) {
          results.failed++
          results.errors.push({ username, message: '密码长度至少为6位' })
          continue
        }

        const [existingUsers] = await pool.query(
          'SELECT id FROM users WHERE username = ?',
          [username]
        )

        if (existingUsers.length > 0) {
          results.failed++
          results.errors.push({ username, message: '用户名已存在' })
          continue
        }

        const hashedPassword = await bcrypt.hash(password, 10)

        await pool.query(
          'INSERT INTO users (username, password, email, role, status) VALUES (?, ?, ?, ?, ?)',
          [username, hashedPassword, email || null, role || 'user', status !== undefined ? status : 1]
        )

        results.success++
      } catch (error) {
        results.failed++
        results.errors.push({ username: userData.username, message: error.message })
      }
    }

    res.json({
      success: true,
      message: `批量导入完成！成功：${results.success} 条，失败：${results.failed} 条`,
      results
    })
  } catch (error) {
    console.error('批量创建用户错误:', error)
    res.status(500).json({ success: false, message: '服务器错误' })
  }
}

module.exports = {
  getUsers,
  createUser,
  updateUser,
  deleteUser,
  batchCreateUsers
}