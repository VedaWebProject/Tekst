import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { defineStore } from 'pinia';
import { useStateStore, useResourcesStore } from '@/stores';
import type { AnyResourceRead, AnyUnitRead, NodeRead } from '@/api';
import { GET } from '@/api';
import { pickTranslation } from '@/utils';
import { $t } from '@/i18n';
import { usePlatformData } from '@/platformData';
import { useMessages } from '@/messages';

export const useBrowseStore = defineStore('browse', () => {
  // composables
  const state = useStateStore();
  const resourcesStore = useResourcesStore();
  const { pfData } = usePlatformData();
  const route = useRoute();
  const router = useRouter();
  const { message } = useMessages();

  /* BASIC BROWSE UI STATE */

  const showResourceToggleDrawer = ref(false);
  const reducedView = ref(false);
  const loadingNodePath = ref(true); // this is intentional!
  const loadingUnits = ref(false);
  const loadingResources = computed(() => resourcesStore.loading);
  const loading = computed(
    () => loadingUnits.value || loadingNodePath.value || resourcesStore.loading
  );

  /* BROWSE LOCATION */

  const nodePath = ref<NodeRead[]>([]);
  const nodePathHead = computed<NodeRead | undefined>(
    () => nodePath.value[nodePath.value.length - 1]
  );
  const level = computed(() => nodePathHead.value?.level ?? state.text?.defaultLevel ?? 0);
  const position = computed(() => nodePathHead.value?.position ?? 0);

  // update browse node path
  async function updateBrowseNodePath(lvl?: string, pos?: string) {
    if (route.name !== 'browse') return;
    loadingNodePath.value = true;
    const qLvl = parseInt(lvl || route.query.lvl?.toString() || '');
    const qPos = parseInt(pos || route.query.pos?.toString() || '');
    if (Number.isInteger(qLvl) && Number.isInteger(qPos)) {
      if (qLvl == nodePathHead.value?.level && qPos == nodePathHead.value?.position) {
        loadingNodePath.value = false;
        return;
      }
      // fill browse node path up to root (no more parent)
      const { data: path, error } = await GET('/browse/nodes/path', {
        params: { query: { textId: state.text?.id || '', level: qLvl, position: qPos } },
      });
      if (!error && path && path.length) {
        nodePath.value = path;
      } else {
        resetBrowseLocation(level.value);
      }
    } else {
      resetBrowseLocation();
    }
    loadingNodePath.value = false;
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
      route.name === 'browse' && resetBrowseLocation();
      nodePath.value = [];
    }
  );

  // react to route changes concerning browse state
  watch([() => route.query.lvl, () => route.query.pos], ([newLvl, newPos]) => {
    if (route.name === 'browse') {
      updateBrowseNodePath(newLvl?.toString(), newPos?.toString());
    }
  });

  // load units data on browse location change
  watch(
    () => nodePathHead.value,
    async () => {
      await loadUnits();
    },
    {
      immediate: true,
    }
  );

  /* RESOURCES AND UNITS */

  const resources = ref<AnyResourceRead[]>([]);
  const resourcesCount = computed(() => resources.value.length);
  const activeResourcesCount = computed(() => resources.value.filter((l) => l.active).length);
  const resourcesCategorized = computed<
    { category: { key: string | undefined; translation: string }; resources: AnyResourceRead[] }[]
  >(() => {
    // compute categorized resources
    const categorized =
      pfData.value?.settings.resourceCategories?.map((c) => ({
        category: { key: c.key, translation: pickTranslation(c.translations, state.locale) },
        resources: resources.value.filter((l) => l.category === c.key),
      })) || [];
    const uncategorized = [
      {
        category: {
          key: undefined,
          translation: $t('browse.uncategorized'),
        },
        resources: resources.value.filter(
          (l) => !categorized.find((c) => c.category.key === l.category)
        ),
      },
    ];
    return [...categorized, ...uncategorized].filter((c) => c.resources.length);
  });

  watch(
    () => resourcesStore.data,
    (newResources) => {
      // process changed available resources
      resources.value =
        newResources.map((l) => {
          const existingResource = resources.value.find((el) => l.id === el.id);
          return {
            ...l,
            active: !existingResource || existingResource.active,
            units: existingResource?.units || [],
          };
        }) || [];
    }
  );

  function setResourceActiveState(resourceId: string, active: boolean) {
    resources.value = resources.value.map((l) => {
      if (l.id === resourceId) {
        return {
          ...l,
          active,
        };
      }
      return l;
    });
  }

  async function loadUnits(nodeIds: string[] = nodePath.value.map((n) => n.id)) {
    if (!nodeIds?.length || !state.text) {
      return;
    }
    loadingUnits.value = true;
    const { data, error } = await GET('/units', {
      params: { query: { nodeId: nodeIds } },
    });
    if (!error) {
      // assign units to resources
      resources.value.forEach((l: AnyResourceRead) => {
        l.units = data.filter((u: AnyUnitRead) => u.resourceId == l.id);
      });
    } else {
      message.error('Error loading resource units for this location', error.detail?.toString());
    }
    loadingUnits.value = false;
  }

  return {
    showResourceToggleDrawer,
    reducedView,
    loading,
    loadingNodePath,
    loadingUnits,
    loadingResources,
    resourcesCount,
    activeResourcesCount,
    resourcesCategorized,
    setResourceActiveState,
    nodePath,
    nodePathHead,
    level,
    position,
    updateBrowseNodePath,
    resetBrowseLocation,
  };
});
