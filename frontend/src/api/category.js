import client from './client';

export const getCategories = () => client.get('categorie/').then(r => r.data);
export const getCategoryAttributes = () => client.get('categorie/attributes/').then(r => r.data);
export const getCategoryFeatures = () => client.get('categorie/features/').then(r => r.data);
