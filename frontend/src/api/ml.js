import client from './client';

export const getPropertyPrice = (data) => client.post('ml/property-price/', data).then(r => r.data);
