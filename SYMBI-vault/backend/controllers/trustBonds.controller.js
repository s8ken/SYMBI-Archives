const TrustBond = require('../models/TrustBond');

exports.createBond = async (req, res) => {
  try {
    const { agentId, scope, consentEnvelope } = req.body;
    const expiresAt = scope?.duration ? new Date(Date.now() + scope.duration*86400000) : scope?.expiresAt;
    const bond = new TrustBond({
      human_user_id: req.user?._id || req.user?.id,
      agent_id: agentId,
      state: 'active',
      scope: { ...scope, expiresAt },
      consent_envelope: consentEnvelope
    });
    bond.calculateTrustScore();
    await bond.save();
    res.status(201).json({ success:true, data: bond });
  } catch (e) { res.status(500).json({ success:false, error:e.message }); }
};

exports.getBond = async (req, res) => {
  const bond = await TrustBond.findById(req.params.id);
  if (!bond) return res.status(404).json({ success:false, error:'Not found' });
  res.json({ success:true, data:bond });
};

exports.updateBond = async (req, res) => {
  const bond = await TrustBond.findById(req.params.id);
  if (!bond) return res.status(404).json({ success:false, error:'Not found' });
  Object.assign(bond, req.body);
  bond.calculateTrustScore();
  await bond.save();
  res.json({ success:true, data:bond });
};

exports.suspendBond = async (req, res) => {
  const bond = await TrustBond.findById(req.params.id);
  if (!bond) return res.status(404).json({ success:false, error:'Not found' });
  await bond.suspend(req.body?.reason || 'suspended', req.user?._id || req.user?.id);
  res.json({ success:true, data:bond });
};

exports.revokeBond = async (req, res) => {
  const bond = await TrustBond.findById(req.params.id);
  if (!bond) return res.status(404).json({ success:false, error:'Not found' });
  await bond.revoke(req.body?.reason || 'revoked', req.user?._id || req.user?.id);
  res.json({ success:true, data:bond });
};
