const mongoose = require('mongoose');

const trustBondSchema = new mongoose.Schema({
  human_user_id: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true, index: true },
  agent_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Agent', required: true, index: true },
  state: { type: String, enum: ['proposed','active','suspended','revoked','expired'], default: 'proposed', index: true },
  scope: {
    purpose: { type: String, required: true },
    dataClasses: [{ type: String, enum: ['public','personal','sensitive','medical','financial'] }],
    permissions: [{ type: String, enum: ['chat.read','chat.write','data.export','analytics.basic','analytics.detailed'] }],
    duration: { type: Number, default: 30 }, // days
    expiresAt: { type: Date, required: true }
  },
  scores: {
    identityConfidence: { type: Number, min: 0, max: 1, default: 0 },
    capabilityDisclosure: { type: Number, min: 0, max: 1, default: 0 },
    compliance: { type: Number, min: 0, max: 1, default: 0 },
    behavior: { type: Number, min: 0, max: 1, default: 0.5 },
    humanFeedback: { type: Number, min: 0, max: 1, default: 0.5 }
  },
  trustScore: { type: Number, min: 0, max: 100, default: 50, index: true },
  trustBand: { type: String, enum: ['Low','Guarded','Elevated','High'], default: 'Guarded' },
  decay: {
    halfLifeDays: { type: Number, default: 14 },
    lastUpdatedAt: { type: Date, default: Date.now },
    decayRate: { type: Number, default: 0.05 }
  },
  evidence: [{
    type: { type: String, enum: ['identity','capability','consent','interaction','violation'], required: true },
    ref: { type: String, required: true },
    hash: { type: String, required: true },
    description: String,
    createdAt: { type: Date, default: Date.now },
    verifiedAt: Date,
    verifiedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' }
  }],
  consent_envelope: {
    termsHash: { type: String, required: true },
    signatures: [{
      actor: { type: String, enum: ['human','agent'], required: true },
      signature: { type: String, required: true },
      timestamp: { type: Date, default: Date.now },
      publicKey: String
    }],
    nonce: { type: String, required: true, unique: true },
    createdAt: { type: Date, default: Date.now }
  },
  history: [{
    at: { type: Date, default: Date.now },
    action: {
      type: String,
      enum: ['created','activated','suspended','revoked','score_updated','evidence_added','consent_amended','violation_detected'],
      required: true
    },
    by: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    notes: String,
    previousState: String,
    newState: String,
    metadata: mongoose.Schema.Types.Mixed
  }],
  violations: [{
    type: { type: String, enum: ['scope_breach','consent_violation','policy_breach','behavior_anomaly'], required: true },
    severity: { type: String, enum: ['low','medium','high','critical'], required: true },
    description: String,
    evidenceRef: String,
    resolvedAt: Date,
    resolvedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    createdAt: { type: Date, default: Date.now }
  }],
  metrics: {
    totalInteractions: { type: Number, default: 0 },
    avgSessionDuration: { type: Number, default: 0 },
    lastInteractionAt: Date,
    satisfactionScore: { type: Number, min: 1, max: 5 }
  }
}, { timestamps: true });

// Indexes
trustBondSchema.index(
  { human_user_id: 1, agent_id: 1 },
  { unique: true, partialFilterExpression: { state: 'active' } }
);
trustBondSchema.index({ state: 1, trustScore: -1 });
trustBondSchema.index({ 'scope.expiresAt': 1 });
trustBondSchema.index({ 'consent_envelope.nonce': 1 }, { unique: true });

// Methods
trustBondSchema.methods.calculateTrustScore = function () {
  const w = { identityConfidence: 0.2, capabilityDisclosure: 0.15, compliance: 0.25, behavior: 0.25, humanFeedback: 0.15 };
  const base = Object.keys(w).reduce((sum, k) => sum + (this.scores[k] * w[k]), 0);
  const days = (Date.now() - this.decay.lastUpdatedAt) / 86400000;
  const decayFactor = Math.exp(-Math.log(2) * days / this.decay.halfLifeDays);
  const finalScore = Math.round(100 * base * decayFactor);
  this.trustScore = Math.max(0, Math.min(100, finalScore));
  this.trustBand = this.trustScore >= 80 ? 'High' : this.trustScore >= 60 ? 'Elevated' : this.trustScore >= 40 ? 'Guarded' : 'Low';
  this.decay.lastUpdatedAt = new Date();
  return this.trustScore;
};

trustBondSchema.methods.addEvidence = function (e) {
  this.evidence.push(e);
  this.addToHistory('evidence_added', null, `Added ${e.type} evidence`);
  return this.save();
};

trustBondSchema.methods.addViolation = function (v) {
  this.violations.push(v);
  const impact = { low: -0.05, medium: -0.1, high: -0.2, critical: -0.4 };
  this.scores.behavior = Math.max(0, this.scores.behavior + impact[v.severity]);
  this.calculateTrustScore();
  this.addToHistory('violation_detected', null, `${v.severity} violation: ${v.type}`);
  return this.save();
};

trustBondSchema.methods.addToHistory = function (action, by, notes, metadata = {}) {
  this.history.push({ action, by, notes, previousState: this.state, metadata });
};

trustBondSchema.methods.suspend = function (reason, by) {
  const prev = this.state; this.state = 'suspended';
  this.addToHistory('suspended', by, reason, { previousState: prev }); return this.save();
};

trustBondSchema.methods.revoke = function (reason, by) {
  const prev = this.state; this.state = 'revoked';
  this.addToHistory('revoked', by, reason, { previousState: prev }); return this.save();
};

trustBondSchema.methods.activate = function (by) {
  const prev = this.state; this.state = 'active';
  this.addToHistory('activated', by, 'Bond activated', { previousState: prev }); return this.save();
};

trustBondSchema.methods.isExpired = function () {
  const exp = this?.scope?.expiresAt ? new Date(this.scope.expiresAt) : null;
  return !!(exp && Date.now() > exp.getTime());
};

trustBondSchema.methods.canPerformAction = function (action) {
  if (this.state !== 'active' || this.isExpired()) return false;
  if (this.trustBand === 'Low' && ['chat.write','data.export'].includes(action)) return false;
  return (this.scope.permissions || []).includes(action);
};

// Statics
trustBondSchema.statics.findActiveBonds = function () {
  return this.find({ state: 'active', 'scope.expiresAt': { $gt: new Date() } });
};
trustBondSchema.statics.findExpiredBonds = function () {
  return this.find({ state: 'active', 'scope.expiresAt': { $lte: new Date() } });
};

// Auto compute expiry if only duration provided
trustBondSchema.pre('validate', function (next) {
  if (this?.scope && !this.scope.expiresAt) {
    const days = Number(this.scope.duration || 30);
    this.scope.expiresAt = new Date(Date.now() + days * 86400000);
  }
  next();
});

module.exports = mongoose.model('TrustBond', trustBondSchema);
