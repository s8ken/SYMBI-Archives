const express = require('express');
const router = express.Router();
const { protect } = require('../middleware/auth.middleware');
const ctrl = require('../controllers/trustBonds.controller');

router.use(protect);
router.post('/', ctrl.createBond);
router.get('/:id', ctrl.getBond);
router.put('/:id', ctrl.updateBond);
router.post('/:id/suspend', ctrl.suspendBond);
router.post('/:id/revoke', ctrl.revokeBond);

module.exports = router;
