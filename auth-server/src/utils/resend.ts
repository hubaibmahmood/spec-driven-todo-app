import { Resend } from 'resend';
import { env } from '../config/env';

// Lazy initialize Resend client
let _resend: Resend | null = null;

export function getResend() {
  if (!_resend) {
    _resend = new Resend(env.RESEND_API_KEY);
  }
  return _resend;
}

// For backwards compatibility
export const resend = new Proxy({} as Resend, {
  get(target, prop) {
    return getResend()[prop as keyof Resend];
  }
});