module.exports = {
  port: process.env.PORT || 3001,
  nodeEnv: process.env.NODE_ENV || 'development',
  cors: {
    origin: '*',
    credentials: true
  },
  upload: {
    maxSize: '10mb'
  }
}