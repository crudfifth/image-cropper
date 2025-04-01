import axios from 'axios';
import AuthTokenRepository from './AuthTokenRepository';
import router from '../router';
import UserRepository from './UserRepository';

const baseURL = `${
  import.meta.env.VITE_APP_API_URL ?? 'https://ihi-backend.bizfreak.co.jp:2343'
}/api/v1`;

const axiosInstance = axios.create({
  baseURL,
});

axiosInstance.interceptors.request.use((config) => {
  const token = AuthTokenRepository.getToken();
  if (token) {
    config.headers.Authorization = 'Bearer ' + token;
  }
  return config;
});

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const path = router.currentRoute.value.path;
    if (path.startsWith('/demo')) {
      return Promise.reject(error);
    }

    const originzalRequest = error.config;
    if (error.response.status === 401 && !originzalRequest._retry) {
      originzalRequest._retry = true;
      const refreshToken = AuthTokenRepository.getRefreshToken();
      if (refreshToken) {
        try {
          const { data } = await axiosInstance.post('token/refresh/', {
            refresh: refreshToken,
          });
          AuthTokenRepository.saveToken(data.access, data.refresh);
          axiosInstance.defaults.headers.common['Authorization'] =
            'Bearer ' + data.access;
          return axiosInstance(originzalRequest);
        } catch (error) {
          UserRepository.removeSelectedCompanyId();
          AuthTokenRepository.removeToken();
          router.push({ name: 'SignIn' });
          return Promise.reject(error);
        }
      } else {
        UserRepository.removeSelectedCompanyId();
        AuthTokenRepository.removeToken();
        router.push({ name: 'SignIn' });
      }
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
