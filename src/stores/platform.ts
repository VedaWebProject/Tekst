import { ref } from 'vue';
import { defineStore } from 'pinia';
import { PlatformApi, type PlatformData } from '@/openapi';
import { useStateStore } from '@/stores';

export const usePlatformStore = defineStore('platform', () => {
  const data = ref<PlatformData>();
  const platformApi = new PlatformApi();
  const state = useStateStore();

  async function loadPlatformData() {
    return platformApi
      .getPlatformData()
      .then((response) => {
        data.value = response.data;
        return response.data;
      })
      .then((data: PlatformData) => {
        // TODO implement storing default text ID
        state.text = data.texts[0];
      });
  }

  return { loadPlatformData, data };
});
