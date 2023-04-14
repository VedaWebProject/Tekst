import { ref } from 'vue';
import { defineStore } from 'pinia';
import { PlatformApi, type PlatformData } from '@/openapi';
import { configureApi } from '@/openApiConfig';

export const usePlatformStore = defineStore('platform', () => {
  const data = ref<PlatformData>();
  const platformApi = configureApi(PlatformApi);

  async function loadPlatformData() {
    return platformApi.getPlatformData().then((response) => {
      data.value = response.data;
      return response.data;
    });
  }

  return { loadPlatformData, data };
});
