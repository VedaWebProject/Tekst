import { ref } from 'vue';
import { configureApi } from './openApiConfig';
import { AdminApi, type PlatformStats } from '@/openapi';
import type { AxiosResponse } from 'axios';

export function useStats() {
  const stats = ref<PlatformStats | null>(null);
  const error = ref(false);
  const adminApi = configureApi(AdminApi);

  function load() {
    stats.value = null;
    error.value = false;
    adminApi
      .stats()
      .then((response: AxiosResponse<PlatformStats, any>) => response.data)
      .then((s: PlatformStats) => (stats.value = s))
      .catch(() => (error.value = true));
  }

  load();

  return { stats, error, load };
}
