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
        const route = router.currentRoute.value;
        const textParam = data.texts.find((t) => t.slug === route.params.text);
        const textStorage = data.texts.find((t) => t.slug == localStorage.getItem('text'));
        const textDefault = data.texts.find((t) => t.id == data.settings.defaultTextId);
        const textFirst = data.texts[0];

        if ('text' in route.params) {
          if (!textParam) {
            router.replace({
              name: route.name || 'browse',
              params: {
                ...route.params,
                text: textStorage?.slug || textDefault?.slug || textFirst.slug,
              },
            });
          } else {
            state.text = textParam || textStorage || textDefault || textFirst;
          }
        } else {
          state.text = textStorage || textDefault || textFirst;
        }
      });
  }

  return { loadPlatformData, data };
});
