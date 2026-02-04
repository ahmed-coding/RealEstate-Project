import client from './client';

export const getFavorites = () => client.get('user/favorite/').then(r => r.data);
export const addFavorite = (data) => client.post('user/favorite/create/', data).then(r => r.data);
export const deleteFavorite = (prop_id) => client.delete(`user/favorite/${prop_id}/delete/`).then(r => r.data);
export const deleteAllFavorites = () => client.post('user/favorite/delete-all/').then(r => r.data);
export const deleteFavoriteList = (data) => client.post('user/favorite/delete-list/', data).then(r => r.data);
