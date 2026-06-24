import api from './api';

export async function getProviders() {
  const { data } = await api.get('/providers');
  return data?.providers ?? [];
}

export async function getRecommendations(payload) {
  const { data } = await api.post('/recommendations', payload);
  return data?.recommendations ?? [];
}
