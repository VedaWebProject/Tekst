import { useAuthStore } from '@/stores';
import axios from 'axios';

axios.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response.status === 401 && !error.response.config.url.endsWith('/logout')) {
      console.log('401 response');
      const auth = useAuthStore();
      if (auth.loggedIn) {
        console.log('Running logout sequence in reaction to 401 response');
        auth.logout();
      }
    }
    return Promise.reject(error);
  }
);
