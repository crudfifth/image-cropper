export default {
  saveRememberMe(isRememberMe: boolean) {
    localStorage.setItem('isRememberMe', String(isRememberMe));
  },
  getRememberMe() {
    return localStorage.getItem('isRememberMe') === 'true';
  },
};
