import { ref } from 'vue';
import { GET } from '@/api';
import type { ClientSegmentRead, PlatformData } from '@/api';

const data = ref<PlatformData>();
const loadedPageSegments = ref<ClientSegmentRead[]>([]);

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
    if (!key) return undefined;
    if (key.startsWith('system')) {
      const segments = data.value?.systemSegments.filter((s) => s.key === key) || [];
      return (
        segments.find((s) => s.locale === locale) ||
        segments.find((s) => !s.locale) ||
        segments.find((s) => s.locale === 'enUS') ||
        segments[0]
      );
    } else {
      const keyMatches = data.value?.pagesInfo.filter((s) => s.key === key) || [];
      const targetSegment =
        keyMatches.find((p) => p.locale === locale) ||
        keyMatches.find((p) => !p.locale) ||
        keyMatches.find((p) => p.locale === 'enUS');
      if (!targetSegment) return undefined;
      const segment = loadedPageSegments.value.find((s) => s.id === targetSegment.id);
      if (segment) return segment;
      const { data: segmentData, error } = await GET('/platform/segments', {
        params: {
          query: {
            key: targetSegment.key,
            ...(targetSegment.locale ? { locale: targetSegment.locale } : {}),
          },
        },
      });
      if (!error) {
        loadedPageSegments.value.push(segmentData);
        return segmentData;
      }
    }
  }

  return { pfData: data, loadPlatformData, getSegment };
}
