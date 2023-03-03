import { ref } from 'vue';
import { defineStore } from 'pinia';
import { PlatformApi, type PlatformData } from '@/openapi';
import { useRouter } from 'vue-router';

export const usePlatformStore = defineStore('platform', () => {
  const data = ref<PlatformData>();
  const platformApi = new PlatformApi();
  const router = useRouter();

  async function loadPlatformData() {
    return platformApi
      .getPlatformData()
      .then((response) => {
        data.value = response.data;
        return response.data;
      })
      .then((data: PlatformData) => {
        // TODO implement storing default text ID
        router.push({
          path: router.currentRoute.value.path,
          query: { ...router.currentRoute.value.query, text: data.texts[0].slug },
        });
      });
  }

  return { loadPlatformData, data };
});
