// App constants
export const COLORS = {
  primary: '#007AFF',
  secondary: '#5856D6',
  success: '#34C759',
  warning: '#FF9500',
  error: '#FF3B30',
  info: '#5AC8FA',
  
  // Text colors
  textPrimary: '#000000',
  textSecondary: '#6D6D70',
  textTertiary: '#8E8E93',
  
  // Background colors
  background: '#F2F2F7',
  backgroundSecondary: '#FFFFFF',
  backgroundTertiary: '#F8F8F8',
  
  // Border colors
  border: '#C7C7CC',
  borderSecondary: '#E5E5EA',
  
  // UIT specific colors
  uitBlue: '#0066CC',
  uitOrange: '#FF6600',
};

export const SIZES = {
  // Font sizes
  fontSmall: 12,
  fontMedium: 16,
  fontLarge: 20,
  fontXLarge: 24,
  fontXXLarge: 32,
  
  // Spacing
  spacingXSmall: 4,
  spacingSmall: 8,
  spacingMedium: 16,
  spacingLarge: 24,
  spacingXLarge: 32,
  
  // Border radius
  radiusSmall: 4,
  radiusMedium: 8,
  radiusLarge: 12,
  radiusXLarge: 16,
  
  // Icon sizes
  iconSmall: 16,
  iconMedium: 24,
  iconLarge: 32,
  iconXLarge: 48,
};

export const FONTS = {
  regular: 'System',
  medium: 'System',
  bold: 'System',
  // You can add custom fonts here when needed
};

export const SCREEN_NAMES = {
  HOME: 'Home',
  LOGIN: 'Login',
  REGISTER: 'Register',
  PROFILE: 'Profile',
  SETTINGS: 'Settings',
  SCHEDULE: 'Schedule',
  GRADES: 'Grades',
  MAP: 'Map',
  NEWS: 'News',
};

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    ME: '/auth/me',
  },
  USER: {
    PROFILE: '/user/profile',
    UPDATE_PROFILE: '/user/profile',
  },
  SCHEDULE: {
    GET_SCHEDULE: '/schedule',
    UPDATE_SCHEDULE: '/schedule',
  },
  GRADES: {
    GET_GRADES: '/grades',
  },
};