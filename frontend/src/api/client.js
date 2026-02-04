import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || '/api';

const client = axios.create({
    baseURL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add a request interceptor to inject the token
client.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Token ${token}`; // Adjusted for Django Token Auth
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default client;
