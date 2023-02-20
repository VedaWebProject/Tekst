import { ref } from 'vue';
import { defineStore } from 'pinia';
import _get from 'lodash.get';
import { PlatformApi } from '@/openapi';

export const usePlatformStore = defineStore('platform', () => {
  const data = ref({});
  const platformApi = new PlatformApi();

  async function loadPlatformData() {
    return platformApi.getPlatformData().then((response) => {
      data.value = response.data;
    });
  }

  function get(platformDataPath: string) {
    return _get(data.value, platformDataPath, '');
  }

  return { loadPlatformData, get };
});
