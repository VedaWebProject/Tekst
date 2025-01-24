import type { AnyResourceRead, LocationRead } from '@/api';
import { GET } from '@/api';
import { $t } from '@/i18n';
import { useResourcesStore, useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

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
  const nextLocationId = ref<string>();
  const prevLocationId = ref<string>();
  const level = computed(() => locationPathHead.value?.level);
  const isOnDefaultLevel = computed(
    () => !state.text || level.value == null || level.value === state.text.defaultLevel
  );
  const position = computed(() => locationPathHead.value?.position ?? 0);

  async function loadLocationData(
    locId: string | undefined = route.params.locId?.toString(),
    force: boolean = false
  ) {
    if (route.name !== 'browse') return;
    loadingLocationData.value = true;
    // do nothing if location data is already loaded and loading is not forced
    if (!force && !!locId && locId === locationPathHead.value?.id) {
      loadingLocationData.value = false;
      return;
    }
    // request location data
    const { data: locationData, error } = await GET('/browse', {
      params: {
        query: locId ? { id: locId } : { txt: state.text?.id },
      },
    });
    if (!error && !!locationData.locationPath?.length) {
      locationPath.value = locationData.locationPath;
      nextLocationId.value = locationData.next || undefined;
      prevLocationId.value = locationData.prev || undefined;
      const textSlug =
        state.textById(locationPath.value[locationPath.value.length - 1]?.textId)?.slug ||
        state.text?.slug ||
        state.defaultText?.slug ||
        '';
      resources.applyContents(locationData.contents);
      // set correct route params in case any were missing or an invalid combination
      if (!locId || !route.params.textSlug || (textSlug && route.params.textSlug !== textSlug)) {
        router.replace({
          name: 'browse',
          params: {
            textSlug: textSlug,
            locId: locationPathHead.value?.id,
          },
        });
      }
    } else {
      // on error, just reset textSlug and empty location ID
      router.replace({
        name: 'browse',
        params: {
          textSlug: state.text?.slug || state.defaultText?.slug || '',
          locId: null,
        },
      });
    }
    loadingLocationData.value = false;
  }

  /* RESOURCES AND CONTENTS */

  const compareResourceOrder = (a: AnyResourceRead, b: AnyResourceRead) => {
    const sortOrderA = a.config.common.sortOrder ?? 0;
    const sortOrderB = b.config.common.sortOrder ?? 0;
    const modA =
      state.pf?.state.prioritizeBrowseLevelResources && level.value !== a.level ? 1001 : 0;
    const modB =
      state.pf?.state.prioritizeBrowseLevelResources && level.value !== b.level ? 1001 : 0;
    return sortOrderA + modA - (sortOrderB + modB);
  };

  const resourcesCategorized = computed<
    { category: { key: string | undefined; translation: string }; resources: AnyResourceRead[] }[]
  >(() => {
    // compute categorized resources
    const categorized =
      state.text?.resourceCategories?.map((c) => ({
        category: { key: c.key, translation: pickTranslation(c.translations, state.locale) },
        resources: resources.ofText
          .filter(
            (r) => r.config.common.category === c.key && (showNonPublicResources.value || r.public)
          )
          .sort(compareResourceOrder),
      })) || [];
    const uncategorized = [
      {
        category: {
          key: undefined,
          translation: $t('browse.uncategorized'),
        },
        resources: resources.ofText.filter(
          (r) =>
            !categorized.find((c) => c.category.key === r.config.common.category) &&
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
    nextLocationId,
    prevLocationId,
    level,
    isOnDefaultLevel,
    position,
    loadLocationData,
  };
});
