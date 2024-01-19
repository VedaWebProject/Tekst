import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { defineStore } from 'pinia';
import { useStateStore, useResourcesStore } from '@/stores';
import type { AnyResourceRead, AnyContentRead, NodeRead } from '@/api';
import { GET } from '@/api';
import { pickTranslation } from '@/utils';
import { $t } from '@/i18n';
import { usePlatformData } from '@/platformData';

export const useBrowseStore = defineStore('browse', () => {
  // composables
  const state = useStateStore();
  const resources = useResourcesStore();
  const { pfData } = usePlatformData();
  const route = useRoute();
  const router = useRouter();

  /* BASIC BROWSE UI STATE */

  const showResourceToggleDrawer = ref(false);
  const reducedView = ref(false);
  const loadingLocationData = ref(true); // this is intentional!
  const loadingResources = computed(() => resources.loading);
  const loading = computed(() => loadingLocationData.value || resources.loading);

  /* BROWSE LOCATION */

  const nodePath = ref<NodeRead[]>([]);
  const nodePathHead = computed<NodeRead | undefined>(
    () => nodePath.value[nodePath.value.length - 1]
  );
  const level = computed(() => nodePathHead.value?.level ?? state.text?.defaultLevel ?? 0);
  const position = computed(() => nodePathHead.value?.position ?? 0);

  // update browse node path
  async function loadLocationData(lvl?: string, pos?: string, force: boolean = false) {
    if (route.name !== 'browse') return;
    loadingLocationData.value = true;
    const qLvl = parseInt(lvl || route.query.lvl?.toString() || '');
    const qPos = parseInt(pos || route.query.pos?.toString() || '');
    if (Number.isInteger(qLvl) && Number.isInteger(qPos)) {
      if (!force && qLvl == nodePathHead.value?.level && qPos == nodePathHead.value?.position) {
        loadingLocationData.value = false;
        return;
      }
      // fill browse node path up to root (no more parent)
      const { data: locationData, error } = await GET('/browse/location-data', {
        params: {
          query: {
            txt: state.text?.id || '',
            lvl: qLvl,
            pos: qPos,
          },
        },
      });
      if (!error && locationData.nodePath?.length) {
        nodePath.value = locationData.nodePath;
        resources.data.forEach((r: AnyResourceRead) => {
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
      ...route,
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
      nodePath.value = [];
      route.name === 'browse' && resetBrowseLocation();
    }
  );

  /* RESOURCES AND CONTENTS */

  const resourcesCount = computed(() => resources.data.length);
  const activeResourcesCount = computed(() => resources.data.filter((r) => r.active).length);
  const resourcesCategorized = computed<
    { category: { key: string | undefined; translation: string }; resources: AnyResourceRead[] }[]
  >(() => {
    // compute categorized resources
    const categorized =
      pfData.value?.settings.resourceCategories?.map((c) => ({
        category: { key: c.key, translation: pickTranslation(c.translations, state.locale) },
        resources: resources.data.filter((r) => r.config?.category === c.key),
      })) || [];
    const uncategorized = [
      {
        category: {
          key: undefined,
          translation: $t('browse.uncategorized'),
        },
        resources: resources.data.filter(
          (r) => !categorized.find((c) => c.category.key === r.config?.category)
        ),
      },
    ];
    return [...categorized, ...uncategorized].filter((c) => c.resources.length);
  });

  function setResourceActiveState(resourceId: string, active: boolean) {
    resources.data = resources.data.map((l) => {
      if (l.id === resourceId) {
        return {
          ...l,
          active,
        };
      }
      return l;
    });
  }

  return {
    showResourceToggleDrawer,
    reducedView,
    loadingLocationData,
    loadingResources,
    loading,
    resourcesCount,
    activeResourcesCount,
    resourcesCategorized,
    setResourceActiveState,
    nodePath,
    nodePathHead,
    level,
    position,
    loadLocationData,
    resetBrowseLocation,
  };
});
