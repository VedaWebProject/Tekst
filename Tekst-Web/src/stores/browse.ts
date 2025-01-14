import type { AnyContentRead, AnyResourceRead, LocationRead } from '@/api';
import { GET } from '@/api';
import { usePlatformData } from '@/composables/platformData';
import { $t } from '@/i18n';
import { useResourcesStore, useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

export const useBrowseStore = defineStore('browse', () => {
  // composables
  const state = useStateStore();
  const { pfData } = usePlatformData();
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
    const targetSlug =
      state.text?.slug ||
      pfData.value?.texts.find((t) => t.id === pfData.value?.state.defaultTextId)?.slug ||
      '';
    // request location data
    const { data: locationData, error } = await GET('/browse/location-data', {
      params: {
        query: locId ? { id: locId } : { txt: state.text?.id },
      },
    });
    if (!error && !!locationData.locationPath?.length) {
      locationPath.value = locationData.locationPath;
      nextLocationId.value = locationData.next || undefined;
      prevLocationId.value = locationData.prev || undefined;
      resources.ofText.forEach((r: AnyResourceRead) => {
        const content =
          locationData.contents?.find((c: AnyContentRead) => c.resourceId === r.id) ||
          locationData.contents?.find((c: AnyContentRead) => c.resourceId === r.originalId);
        r.contents = content ? [content] : [];
      });
      // if the "locId" path param was missing, add it now
      if (!locId) {
        router.replace({
          name: 'browse',
          params: {
            textSlug: targetSlug,
            locId: locationPathHead.value?.id,
          },
        });
      }
    } else {
      // on error, just reset to targetSlug and empty location ID
      router.replace({
        name: 'browse',
        params: {
          textSlug: targetSlug,
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
      pfData.value?.state.prioritizeBrowseLevelResources && level.value !== a.level ? 1001 : 0;
    const modB =
      pfData.value?.state.prioritizeBrowseLevelResources && level.value !== b.level ? 1001 : 0;
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
