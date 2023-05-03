import { readonly, ref } from 'vue';
import type { PlatformData } from '@/openapi';
import { useApi } from '@/api';

const data = ref<PlatformData>();

export function usePlatformData() {
  const { platformApi } = useApi();
  const pfData = readonly(data);

  async function loadPlatformData() {
    return platformApi.getPlatformData().then((response) => {
      data.value = response.data;
      return response.data;
    });
  }

  return { pfData, loadPlatformData };
}
