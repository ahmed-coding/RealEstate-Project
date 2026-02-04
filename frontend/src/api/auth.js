import client from './client';

export const login = (data) => client.post('auth/login/', data).then(r => r.data);
export const logout = () => client.post('auth/logout/').then(r => r.data);
export const signup = (data) => client.post('auth/sginup/', data).then(r => r.data);
