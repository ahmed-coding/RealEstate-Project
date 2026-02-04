import client from './client';

export const getReviews = () => client.get('review/').then(r => r.data);
export const createReview = (data) => client.post('review/create/', data).then(r => r.data);
export const getPropertyReviews = (pkprop) => client.get(`property/${pkprop}/reviews/`).then(r => r.data);
export const createPropertyReview = (pkprop, data) => client.post(`property/${pkprop}/reviews/create/`, data).then(r => r.data);
