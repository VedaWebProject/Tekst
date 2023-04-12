import { ref } from 'vue';
import { defineStore } from 'pinia';
import { PlatformApi, type PlatformData } from '@/openapi';

export const usePlatformStore = defineStore('platform', () => {
  const data = ref<PlatformData>();
  const platformApi = new PlatformApi();

  async function loadPlatformData() {
    return platformApi.getPlatformData().then((response) => {
      data.value = response.data;
      return response.data;
    });
  }

  return { loadPlatformData, data };
});
