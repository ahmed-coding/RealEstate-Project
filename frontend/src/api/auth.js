import client from './client';

export const login = async (data) => {
    const response = await client.post('/auth/login/', data);
    return response.data;
};

export const signup = async (data) => {
    const response = await client.post('/auth/sginup/', data); // Note: explicit 'sginup' typo from API
    return response.data;
};

export const logout = async () => {
    const response = await client.post('/auth/logout/');
    return response.data;
};
