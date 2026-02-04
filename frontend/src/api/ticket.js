import client from './client';

export const createTicket = (data) => client.post('ticket/create/', data).then(r => r.data);
export const getTicketTypes = () => client.get('ticket/ticket-type/').then(r => r.data);
