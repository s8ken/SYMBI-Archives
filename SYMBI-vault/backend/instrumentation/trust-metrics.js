const client = require('prom-client');
const trustEvalCounter = new client.Counter({ name: 'trust_evaluations_total', help: 'Oracle evaluations', labelNames: ['recommendation'] });
const trustViolationCounter = new client.Counter({ name: 'trust_policy_violations_total', help: 'Policy violations', labelNames: ['article','severity'] });

function recordTrustEvaluation(e) {
  try {
    trustEvalCounter.inc({ recommendation: e.recommendation || 'unknown' }, 1);
    (e.violations||[]).forEach(v => trustViolationCounter.inc({ article: v.articleId, severity: v.severity||'unknown' }, 1));
  } catch {}
}
module.exports = { recordTrustEvaluation, register: client.register };
