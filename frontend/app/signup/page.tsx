'use client';
import { FormEvent, useState } from 'react';
import Link from 'next/link';
import { localAuth } from '../../lib/local-auth';

export default function Signup() {
  const [form, setForm] = useState({ name: '', email: '', password: '', student_id: '', department: 'Computer Science', graduation_year: '2027', cgpa: '7.5' });
  const [error, setError] = useState(''); const [busy, setBusy] = useState(false);
  const update = (key: string, value: string) => setForm(current => ({ ...current, [key]: value }));
  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError('');
    try { await localAuth('/auth/register', { ...form, graduation_year: Number(form.graduation_year), cgpa: Number(form.cgpa) }); location.href = '/student/dashboard'; }
    catch (e) { setError(e instanceof Error ? e.message : 'Unable to create account'); }
    finally { setBusy(false); }
  }
  return <main className="auth-page local-auth"><div className="auth-card signup-card"><Link href="/" className="brand local-brand">OMEN<span>.</span></Link><div className="eyebrow">Student registration</div><h1>Start with your <em>signal.</em></h1><p>Your first profile becomes the source for every readiness and skill-gap result.</p><form onSubmit={submit}><label>Full name<input value={form.name} onChange={e => update('name', e.target.value)} required /></label><div className="auth-form-grid"><label>Email<input type="email" value={form.email} onChange={e => update('email', e.target.value)} required /></label><label>Student ID<input value={form.student_id} onChange={e => update('student_id', e.target.value)} required /></label><label>Department<input value={form.department} onChange={e => update('department', e.target.value)} required /></label><label>Graduation year<input type="number" value={form.graduation_year} onChange={e => update('graduation_year', e.target.value)} min="2000" max="2100" required /></label><label>CGPA<input type="number" value={form.cgpa} onChange={e => update('cgpa', e.target.value)} min="0" max="10" step="0.1" required /></label><label>Password<input type="password" value={form.password} onChange={e => update('password', e.target.value)} minLength={8} required /></label></div>{error && <div className="auth-error">{error}</div>}<button className="btn auth-submit" disabled={busy}>{busy ? 'Creating profile...' : 'Create student account'}</button></form><p className="auth-foot">Already registered? <Link href="/login">Sign in</Link></p></div></main>;
}
