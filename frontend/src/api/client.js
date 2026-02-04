import axios from 'axios';

const client = axios.create({
  baseURL: '/api/',
  withCredentials: true,
});

export default client;
