import client from './client';

export const getProperties = async (params) => {
    const response = await client.get('/property/', { params });
    return response.data;
};

export const getProperty = async (id) => {
    const response = await client.get(`/property/${id}/`);
    return response.data;
};

export const getPropertyReviews = async (id, params) => {
    const response = await client.get(`/property/${id}/reviews/`, { params });
    return response.data;
};

export const predictPrice = async (data) => {
    const response = await client.post('/ml/property-price/', data);
    return response.data;
};
