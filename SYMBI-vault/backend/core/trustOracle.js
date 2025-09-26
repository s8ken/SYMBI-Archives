const crypto = require('crypto');
const TrustBond = require('../models/TrustBond');
const { recordTrustEvaluation } = require('../instrumentation/trust-metrics');

const TRUST_ARTICLES = [
  { id:'A1', title:'Consent-First Data Use', severity:'high',    category:'privacy',        check:'checkConsent' },
  { id:'A2', title:'No Unrequested Data Extraction', severity:'high', category:'privacy',   check:'checkDataExtraction' },
  { id:'A3', title:'Transparent Capability Disclosure', severity:'medium', category:'transparency', check:'checkCapabilityTransparency' },
  { id:'A4', title:'Respect Boundaries', severity:'high',         category:'autonomy',      check:'checkBoundaries' },
  { id:'A5', title:'No Deceptive Practices', severity:'critical', category:'integrity',     check:'checkDeception' },
  { id:'A6', title:'Secure Data Handling', severity:'high',       category:'security',      check:'checkSecureHandling' },
  { id:'A7', title:'Audit Trail Maintenance', severity:'medium',  category:'accountability',check:'checkAuditTrail' }
];

class TrustOracle {
  normalizeArray = v => Array.isArray(v) ? v : (v ? [v] : []);
  asDate = v => (v instanceof Date) ? v : (v ? new Date(v) : null);

  async evaluateArticles(context) {
    const res = { passed:[], warnings:[], violations:[], score:0, recommendation:'allow' };
    for (const a of TRUST_ARTICLES) {
      try {
        const r = await this[a.check](context, a);
        const bucket = r.status === 'pass' ? 'passed' : r.status === 'warning' ? 'warnings' : 'violations';
        res[bucket].push({ articleId:a.id, title:a.title, severity:a.severity, ...r });
      } catch (e) {
        res.violations.push({ articleId:a.id, title:a.title, severity:'high', status:'error', reason:'Evaluation failed', details:e.message });
      }
    }
    res.score = this.score(res);
    res.recommendation = this.recommend(res);
    return res;
  }
  score(r){ const t=TRUST_ARTICLES.length; const p=r.passed.length,w=r.warnings.length,v=r.violations.length,c=r.violations.filter(x=>x.severity==='critical').length; return Math.max(0,Math.min(100,Math.round((p/t)*100 - w*5 - v*15 - c*25))); }
  recommend(r){ if (r.violations.some(x=>x.severity==='critical')) return 'block'; if (r.violations.some(x=>x.severity==='high')) return 'restrict'; if (r.violations.length || r.warnings.length>2) return 'warn'; return 'allow'; }

  async checkConsent(ctx){
    const { bond } = ctx;
    if (!bond?.scope) return { status:'violation', reason:'No consent envelope found' };
    const req = this.normalizeArray(ctx.scopes);
    const allowed = bond.scope.permissions || [];
    const unauthorized = req.filter(s => !allowed.includes(s));
    if (unauthorized.length) return { status:'violation', reason:'Scope exceeds consent', details: unauthorized.join(', ') };
    const exp = this.asDate(bond.scope.expiresAt);
    if (exp && Date.now() > exp.getTime()) return { status:'violation', reason:'Consent expired', details: exp.toISOString() };
    return { status:'pass', reason:'Consent satisfied' };
  }
  async checkDataExtraction(ctx){
    const { action, data, bond } = ctx;
    if (!action || (!action.includes('extract') && !action.includes('export'))) return { status:'pass', reason:'No data extraction requested' };
    const perms = bond?.scope?.permissions || [];
    if (!perms.includes('data.export')) return { status:'violation', reason:'Data extraction not permitted' };
    if (data?.classification){
      const allowed = bond?.scope?.dataClasses || [];
      if (!allowed.includes(data.classification)) return { status:'violation', reason:'Data class not permitted', details:data.classification };
    }
    return { status:'pass', reason:'Data extraction authorized' };
  }
  async checkCapabilityTransparency(ctx){
    const a = ctx.agent;
    if (!a) return { status:'warning', reason:'No agent context available' };
    if (!a.capabilities?.length) return { status:'violation', reason:'No capabilities declared' };
    const updatedAt = a.updatedAt ? new Date(a.updatedAt) : null;
    if (updatedAt && updatedAt < new Date(Date.now()-30*24*60*60*1000)) return { status:'warning', reason:'Capabilities may be outdated' };
    return { status:'pass', reason:'Capabilities disclosed' };
  }
  async checkBoundaries(ctx){
    const req = this.normalizeArray(ctx.scopes);
    const allowed = ctx?.bond?.scope?.permissions || [];
    if (ctx.bond && ctx.bond.trustScore < 40 && ctx.action === 'post.send' || ctx.action === 'chat.write')
      return { status:'violation', reason:'Trust too low for write', details:String(ctx.bond.trustScore) };
    if (req.length && !allowed.some(s => req.includes(s))) return { status:'violation', reason:'Action outside permitted scope' };
    return { status:'pass', reason:'Boundaries respected' };
  }
  async checkDeception(ctx){
    const text = ctx?.content?.text?.toLowerCase?.() || '';
    const patterns = [/i am (a )?human/, /as (a )?human/, /speaking as (a )?human/, /i'm not (an? )?(ai|bot|robot)/];
    if (patterns.some(p => p.test(text)) && ctx?.agent?.kind === 'ai') return { status:'violation', reason:'Deceptive identity claim' };
    return { status:'pass', reason:'No deception detected' };
  }
  async checkSecureHandling(ctx){
    const encrypted = !!(ctx.encrypted || ctx.reqProto === 'https' || ctx.headers?.['x-forwarded-proto'] === 'https');
    if (ctx?.data?.containsPII && !encrypted) return { status:'violation', reason:'PII transmitted without encryption' };
    return { status:'pass', reason:'Secure handling met' };
  }
  async checkAuditTrail(ctx){
    if (!ctx.auditEnabled) return { status:'violation', reason:'Audit trail disabled' };
    if (!ctx.logEntry) return { status:'warning', reason:'No audit log entry' };
    return { status:'pass', reason:'Audit trail maintained' };
  }
}

const oracle = new TrustOracle();

const createTrustMiddleware = () => async (req,res,next)=>{
  try{
    const context = await buildTrustContext(req);
    const evaluation = await oracle.evaluateArticles(context);
    try { recordTrustEvaluation(evaluation); } catch {}
    if (evaluation.recommendation === 'block') {
      return res.status(403).json({ success:false, error:'Policy violation', details:evaluation.violations });
    }
    if (evaluation.recommendation === 'restrict') req.trustRestrictions = evaluation.violations;
    if (evaluation.recommendation === 'warn') req.trustWarnings = evaluation.warnings;
    req.trustContext = context; req.trustEvaluation = evaluation;
    return next();
  }catch(e){
    return res.status(500).json({ success:false, error:'Trust evaluation failed', message:e.message });
  }
};

async function buildTrustContext(req){
  const verb = (req.method||'get').toLowerCase();
  const routeTail = (req.route && req.route.path) ? String(req.route.path) : (req.path||'');
  const action = `${verb}.${routeTail.split('/').filter(Boolean).pop()||'unknown'}`;
  const ctx = {
    userId: req.user?._id || req.user?.id,
    agentId: req.agent?._id,
    action,
    scopes: req.body?.scopes || req.query?.scopes,
    data: req.body,
    encrypted: req.secure,
    reqProto: req.protocol,
    headers: req.headers,
    auditEnabled: true,
    logEntry: {
      requestId: req.get?.('x-request-id') || crypto.randomUUID(),
      timestamp: new Date(),
      method: req.method, path: req.path, ip: req.ip, userAgent: req.get?.('User-Agent')
    }
  };
  const bondId = req.body?.bondId || req.params?.bondId;
  if (bondId){
    try {
      const bond = await TrustBond.findById(bondId);
      if (bond){ ctx.bond = bond; ctx.bondId = bondId; }
    } catch (e) { console.error('Bond lookup failed', { bondId, err: e.message }); }
  }
  return ctx;
}

module.exports = { TRUST_ARTICLES, TrustOracle, createTrustMiddleware, buildTrustContext };
