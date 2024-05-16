import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { defineStore } from 'pinia';
import { useStateStore, useResourcesStore } from '@/stores';
import type { AnyResourceRead, AnyContentRead, LocationRead } from '@/api';
import { GET } from '@/api';
import { pickTranslation } from '@/utils';
import { $t } from '@/i18n';

export const useBrowseStore = defineStore('browse', () => {
  // composables
  const state = useStateStore();
  const resources = useResourcesStore();
  const route = useRoute();
  const router = useRouter();

  /* BASIC BROWSE UI STATE */

  const showResourceToggleDrawer = ref(false);
  const showNonPublicResources = ref(true);
  const reducedView = ref(false);
  const loadingLocationData = ref(true); // this is intentional!
  const loadingResources = computed(() => resources.loading);
  const loading = computed(() => loadingLocationData.value || resources.loading);

  /* BROWSE LOCATION */

  const locationPath = ref<LocationRead[]>([]);
  const locationPathHead = computed<LocationRead | undefined>(
    () => locationPath.value[locationPath.value.length - 1]
  );
  const level = computed(() => locationPathHead.value?.level ?? state.text?.defaultLevel ?? 0);
  const position = computed(() => locationPathHead.value?.position ?? 0);

  // update browse location path
  async function loadLocationData(lvl?: string, pos?: string, force: boolean = false) {
    if (route.name !== 'browse') return;
    loadingLocationData.value = true;
    const qLvl = parseInt(lvl || route.query.lvl?.toString() || '');
    const qPos = parseInt(pos || route.query.pos?.toString() || '');
    if (Number.isInteger(qLvl) && Number.isInteger(qPos)) {
      if (
        !force &&
        qLvl == locationPathHead.value?.level &&
        qPos == locationPathHead.value?.position
      ) {
        loadingLocationData.value = false;
        return;
      }
      // fill browse location path up to root (no more parent)
      const { data: locationData, error } = await GET('/browse/location-data', {
        params: {
          query: {
            txt: state.text?.id || '',
            lvl: qLvl,
            pos: qPos,
          },
        },
      });
      if (!error && locationData.locationPath?.length) {
        locationPath.value = locationData.locationPath;
        resources.ofText.forEach((r: AnyResourceRead) => {
          const content =
            locationData.contents?.find((u: AnyContentRead) => u.resourceId === r.id) ||
            locationData.contents?.find((u: AnyContentRead) => u.resourceId === r.originalId);
          r.contents = content ? [content] : [];
        });
      } else {
        loadingLocationData.value = false;
        resetBrowseLocation(level.value);
      }
    } else {
      loadingLocationData.value = false;
      resetBrowseLocation();
    }
    loadingLocationData.value = false;
  }

  // reset browse location (change URI parameters)
  function resetBrowseLocation(
    level: number = state.text?.defaultLevel || 0,
    position: number = 0,
    text: string = state.fallbackText?.slug || ''
  ) {
    router.replace({
      name: 'browse',
      params: {
        text: text,
      },
      query: {
        ...route.query,
        lvl: level,
        pos: position,
      },
    });
  }

  // set browse location to text default when text changes
  watch(
    () => state.text,
    () => {
      locationPath.value = [];
      route.name === 'browse' && resetBrowseLocation();
    }
  );

  /* RESOURCES AND CONTENTS */

  const resourcesCategorized = computed<
    { category: { key: string | undefined; translation: string }; resources: AnyResourceRead[] }[]
  >(() => {
    // compute categorized resources
    const categorized =
      state.text?.resourceCategories?.map((c) => ({
        category: { key: c.key, translation: pickTranslation(c.translations, state.locale) },
        resources: resources.ofText.filter(
          (r) => r.config?.common?.category === c.key && (showNonPublicResources.value || r.public)
        ),
      })) || [];
    const uncategorized = [
      {
        category: {
          key: undefined,
          translation: $t('browse.uncategorized'),
        },
        resources: resources.ofText.filter(
          (r) =>
            !categorized.find((c) => c.category.key === r.config?.common?.category) &&
            (showNonPublicResources.value || r.public)
        ),
      },
    ];
    return [...categorized, ...uncategorized].filter((c) => c.resources.length);
  });

  return {
    showResourceToggleDrawer,
    reducedView,
    showNonPublicResources,
    loadingLocationData,
    loadingResources,
    loading,
    resourcesCategorized,
    setResourcesActiveState: resources.setResourcesActiveState,
    locationPath,
    locationPathHead,
    level,
    position,
    loadLocationData,
    resetBrowseLocation,
  };
});
