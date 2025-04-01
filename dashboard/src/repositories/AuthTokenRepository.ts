import RememberMeRepository from './RememberMeRepository';
const ACCESS_TOKEN = 'apiToken';
const REFRESH_TOKEN = 'apiRefreshToken';

export default {
  saveToken(token: string, refresh: string) {
    const isRememberMe = RememberMeRepository.getRememberMe();
    localStorage.removeItem(ACCESS_TOKEN);
    localStorage.removeItem(REFRESH_TOKEN);
    sessionStorage.setItem(ACCESS_TOKEN, token);
    sessionStorage.setItem(REFRESH_TOKEN, refresh);
    if (isRememberMe) {
      localStorage.setItem(ACCESS_TOKEN, token);
      localStorage.setItem(REFRESH_TOKEN, refresh);
    }
  },
  getToken() {
    return (
      sessionStorage.getItem(ACCESS_TOKEN) ?? localStorage.getItem(ACCESS_TOKEN)
    );
  },
  getRefreshToken() {
    return (
      sessionStorage.getItem(REFRESH_TOKEN) ??
      localStorage.getItem(REFRESH_TOKEN)
    );
  },
  removeToken() {
    localStorage.removeItem(ACCESS_TOKEN);
    localStorage.removeItem(REFRESH_TOKEN);
    sessionStorage.removeItem(ACCESS_TOKEN);
    sessionStorage.removeItem(REFRESH_TOKEN);
  },
};
