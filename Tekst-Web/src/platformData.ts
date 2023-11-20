import { computed, ref } from 'vue';
import { GET } from '@/api';
import type { ClientSegmentRead, PlatformData } from '@/api';
import _mergeWith from 'lodash.mergewith';

const pfData = ref<PlatformData>();
const loadedInfoSegments = ref<ClientSegmentRead[]>([]);

export function usePlatformData() {
  const systemHome = computed(
    () => pfData.value?.systemSegments.find((p) => p.key === 'systemHome')
  );

  async function _cleanLoadedInfoSegments() {
    loadedInfoSegments.value = loadedInfoSegments.value.filter(
      (p) => !!pfData.value?.infoSegments.find((pi) => pi.id === p.id)
    );
  }

  async function loadPlatformData() {
    const { data: apiData, error } = await GET('/platform', {});
    if (!error) {
      pfData.value = apiData;
      _cleanLoadedInfoSegments();
      return apiData;
    } else {
      throw error;
    }
  }

  function getSegmentId(key?: string, locale?: string) {
    if (!key) return undefined;
    if (key.startsWith('system')) {
      const segments = pfData.value?.systemSegments.filter((s) => s.key === key) || [];
      return (
        segments.find((s) => s.locale === locale) ||
        segments.find((s) => !s.locale) ||
        segments.find((s) => s.locale === 'enUS') ||
        segments[0]
      )?.id;
    } else {
      const keyMatches = pfData.value?.infoSegments.filter((s) => s.key === key) || [];
      return (
        keyMatches.find((p) => p.locale === locale) ||
        keyMatches.find((p) => !p.locale) ||
        keyMatches.find((p) => p.locale === 'enUS')
      )?.id;
    }
  }

  async function getSegment(key?: string, locale?: string) {
    if (!key) return undefined;
    const targetId = getSegmentId(key, locale);
    if (!targetId) return undefined;
    if (key.startsWith('system')) {
      return pfData.value?.systemSegments.find((s) => s.id === targetId);
    } else {
      const segment = loadedInfoSegments.value.find((s) => s.id === targetId);
      if (segment) return segment;
      const { data: segmentData, error } = await GET('/platform/segments/{id}', {
        params: {
          path: {
            id: targetId,
          },
        },
      });
      if (!error) {
        loadedInfoSegments.value.push(segmentData);
        return segmentData;
      }
    }
  }

  function patchPfData(updates: Record<string, any>) {
    _mergeWith(pfData.value, updates, (_, srcValue) => {
      if (Array.isArray(srcValue)) {
        return srcValue;
      }
    });
    _cleanLoadedInfoSegments();
  }

  return { pfData, loadPlatformData, getSegment, patchPfData, systemHome };
}
