// Discord authentication utilities with URL mapping support

export const authUrls = {
  // Core auth endpoints
  login: '/api/auth/discord',
  logout: '/api/logout',
  
  // Custom redirect URLs - map destinations to auth URLs
  dashboard: '/api/auth/discord?returnTo=/dashboard',
  security: '/api/auth/discord?returnTo=/dashboard',
  analytics: '/api/auth/discord?returnTo=/dashboard',
  profile: '/api/auth/discord?returnTo=/profile',
  settings: '/api/auth/discord?returnTo=/settings',
} as const;

export const createAuthUrl = (returnTo: string): string => {
  return `/api/auth/discord?returnTo=${encodeURIComponent(returnTo)}`;
};

export const redirectToAuth = (returnTo?: string): void => {
  const url = returnTo ? createAuthUrl(returnTo) : authUrls.login;
  window.location.href = url;
};

export const redirectToDashboard = (): void => {
  redirectToAuth('/dashboard');
};

export const redirectToSecurity = (): void => {
  redirectToAuth('/dashboard');
};

// Check if user has Discord permissions for specific features
export const hasDiscordPermissions = (user: any, feature: string): boolean => {
  // TODO: Implement Discord role/permission checking
  return !!user;
};

export const getDiscordAvatarUrl = (user: any): string => {
  if (!user?.avatar) return '/default-avatar.png';
  return `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png`;
};

export const getDiscordUsername = (user: any): string => {
  if (!user) return 'Unknown User';
  return user.discriminator && user.discriminator !== '0' 
    ? `${user.username}#${user.discriminator}`
    : user.username;
};