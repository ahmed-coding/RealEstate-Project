import client from './client';

export const getProperties = () => client.get('property/').then(r => r.data);
export const getProperty = (id) => client.get(`property/${id}/`).then(r => r.data);
export const createProperty = (data) => client.post('property/create/', data).then(r => r.data);
export const updateProperty = (id, data) => client.put(`property/${id}/update/`, data).then(r => r.data);
export const deleteProperty = (id) => client.delete(`property/${id}/delete/`).then(r => r.data);
