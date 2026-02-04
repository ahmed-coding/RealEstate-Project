import client from './client';

export const getUserProfile = () => client.get('user/profile/').then(r => r.data);
export const getUserProfileById = (id) => client.get(`user/profile/${id}/`).then(r => r.data);
export const updateUserProfile = (data) => client.put('user/profile/update/', data).then(r => r.data);
