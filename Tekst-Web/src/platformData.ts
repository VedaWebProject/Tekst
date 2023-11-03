import { ref } from 'vue';
import { GET } from '@/api';
import type { ClientSegmentRead, PlatformData } from '@/api';

const data = ref<PlatformData>();
const pageSegments = ref<ClientSegmentRead[]>([]);

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

  async function getSegment(key?: string, locale?: string) {
    if (!key) return null;
    if (key.startsWith('system_')) {
      const segments = data.value?.systemSegments.filter((s) => s.key === key) || [];
      return (
        segments.find((s) => s.locale === locale) ||
        segments.find((s) => s.locale === 'enUS') ||
        segments[0] ||
        null
      );
    } else {
      const segment = pageSegments.value.find((s) => s.key === key && s.locale === locale);
      if (segment) return segment;
      const { data, error } = await GET('/platform/segments', {
        params: { query: { key, ...(locale ? { locale } : {}) } },
      });
      if (!error) {
        pageSegments.value.push(data);
        return data;
      } else {
        console.error(`Error loading segment ${key}`, error);
      }
    }
  }

  return { pfData: data, loadPlatformData, getSegment };
}
