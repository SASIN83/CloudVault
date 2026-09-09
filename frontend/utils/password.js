export function passwordError(pw) {
  if (pw.length < 8) return 'Password must be at least 8 characters';
  if (!/[A-Za-z]/.test(pw)) return 'Password must contain at least one letter';
  if (!/\d/.test(pw)) return 'Password must contain at least one number';
  if (!/[^A-Za-z0-9\s]/.test(pw)) return 'Password must contain at least one special character (e.g. !@#$%)';
  if (/\s/.test(pw)) return 'Password must not contain spaces';
  return '';
}