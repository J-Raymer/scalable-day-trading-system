import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const setupAxiosInterceptors = (navigate: ReturnType<typeof useNavigate>) => {
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
