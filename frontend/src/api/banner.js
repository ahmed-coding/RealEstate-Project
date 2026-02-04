import client from './client';

export const getBanners = () => client.get('banners/').then(r => r.data);
export const createBanner = (data) => client.post('banners/create/', data).then(r => r.data);
