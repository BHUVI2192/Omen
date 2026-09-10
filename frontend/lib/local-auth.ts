const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export type AuthResponse = { access_token: string; student: { name: string; email: string } };

export async function localAuth(path: string, payload: object): Promise<AuthResponse> {
  const response = await fetch(`${API}${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  const body = await response.json();
  if (!response.ok) throw new Error(typeof body.detail === 'string' ? body.detail : 'Unable to complete authentication');
  localStorage.setItem('omen_access_token', body.access_token);
  return body;
}

export function localToken() { return typeof window === 'undefined' ? null : localStorage.getItem('omen_access_token'); }
export function clearLocalToken() { localStorage.removeItem('omen_access_token'); }