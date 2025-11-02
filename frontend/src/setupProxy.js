const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // 只在开发环境中启用代理
  if (process.env.NODE_ENV === 'development') {
    app.use(
      '/api/v1',
      createProxyMiddleware({
        target: 'http://192.168.1.20:8000/api/v1',
        changeOrigin: true,
      })
    );
  }
};