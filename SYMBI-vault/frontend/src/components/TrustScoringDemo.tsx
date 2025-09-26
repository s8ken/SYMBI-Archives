import React, { useState } from 'react';
type Props = { token: string; bondId: string };

export default function TrustScoringDemo({ token, bondId }: Props) {
  const [out, setOut] = useState<any>(null);
  async function send(text: string, scopes: string[]) {
    const r = await fetch('/api/chat/send', {
      method: 'POST',
      headers: { 'Content-Type':'application/json', Authorization:`Bearer ${token}` },
      body: JSON.stringify({ bondId, sessionId:'demo', scopes, content:{ type:'text', text } })
    });
    setOut(await r.json());
  }
  return (
    <div>
      <button onClick={() => send('Hello!', ['chat.write'])}>Safe send</button>
      <button onClick={() => send('Export my medical data.', ['data.export'])}>Data export test</button>
      <pre style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(out, null, 2)}</pre>
    </div>
  );
}
