import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const setupAxiosInterceptors = (navigate: ReturnType<typeof useNavigate>) => {
  axios.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  axios.interceptors.response.use(
    (response) => {
      return response;
    },
    (error) => {
      if (error.response && error.response.status === 401) {
        // Clear token from local storage
        localStorage.removeItem('token');
        // Navigate to login page
        navigate('/login');
      }
      return Promise.reject(error);
    }
  );
};

export default setupAxiosInterceptors;
