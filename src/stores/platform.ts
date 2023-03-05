import { ref } from 'vue';
import { defineStore } from 'pinia';
import { PlatformApi, type PlatformData } from '@/openapi';
import { useRouter } from 'vue-router';
import { useStateStore } from './state';

export const usePlatformStore = defineStore('platform', () => {
  const data = ref<PlatformData>();
  const platformApi = new PlatformApi();
  const router = useRouter();
  const state = useStateStore();

  async function loadPlatformData() {
    return platformApi
      .getPlatformData()
      .then((response) => {
        data.value = response.data;
        return response.data;
      })
      .then((data: PlatformData) => {
        // select default text if none is set
        // TODO implement storing default text ID
        const route = router.currentRoute.value;
        if ('text' in route.params) {
          router.replace({
            name: route.name || 'browse',
            params: {
              ...route.params,
              text: route.params.text || data.texts[0].slug,
            },
          });
        } else {
          state.text = data.texts[0];
        }
      });
  }

  return { loadPlatformData, data };
});
