import { ref } from 'vue';
import { GET } from '@/api';
import type { ClientSegmentRead, PlatformData } from '@/api';
import _mergeWith from 'lodash.mergewith';

const pfData = ref<PlatformData>();
const loadedPageSegments = ref<ClientSegmentRead[]>([]);

export function usePlatformData() {
  async function _cleanLoadedPageSegments() {
    loadedPageSegments.value = loadedPageSegments.value.filter(
      (p) => !!pfData.value?.pagesInfo.find((pi) => pi.id === p.id)
    );
  }

  async function loadPlatformData() {
    const { data: apiData, error } = await GET('/platform', {});
    if (!error) {
      pfData.value = apiData;
      _cleanLoadedPageSegments();
      return apiData;
    } else {
      throw error;
    }
  }

  async function getSegment(key?: string, locale?: string) {
    if (!key) return undefined;
    if (key.startsWith('system')) {
      const segments = pfData.value?.systemSegments.filter((s) => s.key === key) || [];
      return (
        segments.find((s) => s.locale === locale) ||
        segments.find((s) => !s.locale) ||
        segments.find((s) => s.locale === 'enUS') ||
        segments[0]
      );
    } else {
      const keyMatches = pfData.value?.pagesInfo.filter((s) => s.key === key) || [];
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

  function overridePfData(updates: Record<string, any>) {
    _mergeWith(pfData.value, updates, (_, srcValue) => {
      if (Array.isArray(srcValue)) {
        return srcValue;
      }
    });
  }

  return { pfData, loadPlatformData, getSegment, overridePfData };
}
