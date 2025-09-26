import React, { useEffect, useState } from 'react';
type Props = { token: string; bondId: string };

export default function TrustDashboard({ token, bondId }: Props) {
  const [resp, setResp] = useState<any>(null);
  useEffect(() => {
    fetch(`/api/trust/bonds/${bondId}`, { headers: { Authorization: `Bearer ${token}` }})
      .then(r => r.json()).then(setResp).catch(console.error);
  }, [bondId, token]);
  const b = resp?.data;
  if (!b) return <div>Loading trust…</div>;
  return (
    <div>
      <h3>Trust Score: {b.trustScore} ({b.trustBand})</h3>
      <div>Purpose: {b.scope?.purpose}</div>
      <div>Permissions: {(b.scope?.permissions||[]).join(', ')}</div>
      <div>Expires: {b.scope?.expiresAt ? new Date(b.scope.expiresAt).toLocaleString() : 'n/a'}</div>
    </div>
  );
}
