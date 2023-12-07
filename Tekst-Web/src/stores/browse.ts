import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { defineStore } from 'pinia';
import { useStateStore, useLayersStore } from '@/stores';
import type { NodeRead } from '@/api';
import { GET } from '@/api';
import { pickTranslation } from '@/utils';
import { $t } from '@/i18n';
import { usePlatformData } from '@/platformData';

export const useBrowseStore = defineStore('browse', () => {
  // composables
  const state = useStateStore();
  const layersStore = useLayersStore();
  const { pfData } = usePlatformData();
  const route = useRoute();
  const router = useRouter();

  /* BASIC BROWSE UI STATE */

  const showLayerToggleDrawer = ref(false);
  const reducedView = ref(false);
  const loadingNodePath = ref(true); // this is intentional!
  const loading = computed(() => loadingNodePath.value || layersStore.loading);

  /* BROWSE NODE PATH */

  const nodePath = ref<NodeRead[]>([]);
  const nodePathHead = computed(() =>
    nodePath.value.length > 0 ? nodePath.value[nodePath.value.length - 1] : undefined
  );
  const nodePathRoot = computed(() => (nodePath.value.length > 0 ? nodePath.value[0] : undefined));
  const level = computed(() =>
    nodePathHead.value?.level !== undefined
      ? nodePathHead.value.level
      : state.text?.defaultLevel || 0
  );
  const position = computed(() => nodePathHead.value?.position);

  // update browse node path
  async function updateBrowseNodePath(lvl?: string, pos?: string) {
    if (route.name !== 'browse') return;
    loadingNodePath.value = true;
    const qLvl = parseInt(lvl || route.query.lvl?.toString() || '');
    const qPos = parseInt(pos || route.query.pos?.toString() || '');
    if (Number.isInteger(qLvl) && Number.isInteger(qPos)) {
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

  /* LAYERS AND UNITS */

  const layersCount = computed(() => layersStore.data.length);
  const activeLayersCount = computed(() => layersStore.data.filter((l) => l.active).length);
  const layersCategorized = computed(() => {
    const categorized =
      pfData.value?.settings.layerCategories?.map((c) => ({
        category: { key: c.key, translation: pickTranslation(c.translations, state.locale) },
        layers: layersStore.data.filter((l) => l.category === c.key),
      })) || [];
    const uncategorized = [
      {
        category: {
          key: undefined,
          translation: $t('browse.uncategorized'),
        },
        layers: layersStore.data.filter(
          (l) => !categorized.find((c) => c.category.key === l.category)
        ),
      },
    ];
    return [...categorized, ...uncategorized].filter((c) => c.layers.length);
  });

  function activateLayer(id: string) {
    layersStore.data = layersStore.data.map((l) => (l.id === id ? { ...l, active: true } : l));
  }

  function deactivateLayer(id: string) {
    layersStore.data = layersStore.data.map((l) => (l.id === id ? { ...l, active: false } : l));
  }

  // load units data on browse location change
  watch(
    () => nodePathHead.value,
    async () => {
      const nodeIds = nodePath.value.map((n) => n.id);
      if (!nodeIds.length) return;
      // fetch units data
      await layersStore.loadUnits(nodeIds);
    },
    {
      immediate: true,
    }
  );

  return {
    showLayerToggleDrawer,
    reducedView,
    loading,
    layersCount,
    activeLayersCount,
    layersCategorized,
    activateLayer,
    deactivateLayer,
    nodePath,
    nodePathHead,
    nodePathRoot,
    level,
    position,
    updateBrowseNodePath,
    resetBrowseLocation,
  };
});
