require('dotenv').config()
const express = require('express')
const cors = require('cors')
const bodyParser = require('body-parser')
const config = require('./config/index.cjs')
const authRoutes = require('./routes/authRoutes.cjs')
const userRoutes = require('./routes/userRoutes.cjs')
const videoRoutes = require('./routes/videoRoutes.cjs')
const crawlRoutes = require('./routes/crawlRoutes.cjs')
const commentRoutes = require('./routes/commentRoutes.cjs')

const app = express()

app.use(cors(config.cors))
app.use(bodyParser.json())
app.use(bodyParser.urlencoded({ extended: true }))

app.use('/api', authRoutes)
app.use('/api/users', userRoutes)
app.use('/api/videos', videoRoutes)
app.use('/api', crawlRoutes)
app.use('/api', commentRoutes)

app.listen(config.port, () => {
  console.log(`服务器运行在 http://localhost:${config.port}`)
})