'use client';
import { FormEvent, useState } from 'react';
import Link from 'next/link';
import { localAuth } from '../../lib/local-auth';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError('');
    try { await localAuth('/auth/login', { email, password }); location.href = '/student/dashboard'; }
    catch (e) { setError(e instanceof Error ? e.message : 'Unable to sign in'); }
    finally { setBusy(false); }
  }
  return <main className="auth-page local-auth"><div className="auth-card"><Link href="/" className="brand local-brand">OMEN<span>.</span></Link><div className="eyebrow">Student workspace</div><h1>Welcome <em>back.</em></h1><p>Sign in to see the readiness signal built from your profile, skills, and learning progress.</p><form onSubmit={submit}><label>Email<input type="email" value={email} onChange={e => setEmail(e.target.value)} required /></label><label>Password<input type="password" value={password} onChange={e => setPassword(e.target.value)} required /></label>{error && <div className="auth-error">{error}</div>}<button className="btn auth-submit" disabled={busy}>{busy ? 'Signing in...' : 'Sign in'}</button></form><p className="auth-foot">New student? <Link href="/signup">Create an account</Link></p></div></main>;
}
