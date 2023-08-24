import { ref } from 'vue';
import { GET } from '@/api';
import type { PlatformData } from '@/api';

const data = ref<PlatformData>();

export function usePlatformData() {
  async function loadPlatformData() {
    const { data: apiData, error } = await GET('/platform', {});
    if (!error) {
      data.value = apiData;
      return apiData;
    } else {
      throw error;
    }
  }
  return { pfData: data, loadPlatformData };
}
