import client from './client';

export const getCountries = () => client.get('address/country/').then(r => r.data);
export const getStates = () => client.get('address/state/').then(r => r.data);
export const getCities = () => client.get('address/city/').then(r => r.data);
export const createAddress = (data) => client.post('address/create/', data).then(r => r.data);
export const updateAddress = (id, data) => client.put(`address/${id}/update/`, data).then(r => r.data);
