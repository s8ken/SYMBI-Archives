# Wire the Trust Oracle into your “send” route

1) Import in your chat route file:
   `const { createTrustMiddleware } = require('../core/trustOracle');`

2) Add middleware before the controller:
   `router.post('/send', createTrustMiddleware(), controller.sendMessage);`

3) Expose metrics in your Express app:
```js
const bondRoutes = require('./routes/trust-bonds.routes');
const { register } = require('./instrumentation/trust-metrics');
app.use('/api/trust/bonds', bondRoutes);
app.get('/metrics', async (_req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});
```
