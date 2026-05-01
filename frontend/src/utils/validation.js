export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

export const validatePassword = (password) => {
  const errors = [];
  
  if (password.length < 8) {
    errors.push('Password must be at least 8 characters');
  }
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }
  if (!/[0-9]/.test(password)) {
    errors.push('Password must contain at least one number');
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
};

export const validateProjectName = (name) => {
  if (!name || name.trim().length === 0) {
    return { isValid: false, error: 'Project name is required' };
  }
  if (name.length < 3) {
    return { isValid: false, error: 'Project name must be at least 3 characters' };
  }
  if (name.length > 100) {
    return { isValid: false, error: 'Project name must be less than 100 characters' };
  }
  return { isValid: true };
};

export const validateFileSize = (file, maxSizeMB = 100) => {
  const maxBytes = maxSizeMB * 1024 * 1024;
  if (file.size > maxBytes) {
    return {
      isValid: false,
      error: `File size must be less than ${maxSizeMB}MB`,
    };
  }
  return { isValid: true };
};

export const validateFileType = (file, allowedTypes = ['.zip']) => {
  const fileName = file.name.toLowerCase();
  const isValid = allowedTypes.some(type => fileName.endsWith(type));
  
  if (!isValid) {
    return {
      isValid: false,
      error: `Only ${allowedTypes.join(', ')} files are allowed`,
    };
  }
  return { isValid: true };
};

export const sanitizeInput = (input) => {
  if (typeof input !== 'string') return input;
  
  return input
    .trim()
    .replace(/[<>]/g, '') // Remove potential HTML tags
    .slice(0, 10000); // Limit length
};

// Made with Bob
