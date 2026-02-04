import client from './client';

export const createAlarm = (data) => client.post('user/alarms/create', data).then(r => r.data);
