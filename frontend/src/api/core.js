import client from './client';

export const getBanners = async (params) => {
    const response = await client.get('/banners/', { params });
    return response.data;
};

export const getCategories = async (params) => {
    const response = await client.get('/categorie/', { params });
    return response.data;
};

export const getStates = async (params) => {
    const response = await client.get('/address/state/', { params });
    return response.data;
};
