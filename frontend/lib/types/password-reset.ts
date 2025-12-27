/**
 * Type definitions for password reset feature
 */

import { PasswordValidation } from '../validation/password';

/**
 * Form state for forgot password page
 */
export interface ForgotPasswordFormState {
  email: string;
  isLoading: boolean;
  error: string | null;
  successMessage: string | null;
  rateLimitRemaining: number | null;
}

/**
 * Form state for reset password page
 */
export interface ResetPasswordFormState {
  newPassword: string;
  confirmPassword: string;
  token: string | null;
  tokenError: string | null;
  isLoading: boolean;
  showPassword: boolean;
  showConfirmPassword: boolean;
  error: string | null;
  passwordValidation: PasswordValidation | null;
  passwordsMatch: boolean;
}
