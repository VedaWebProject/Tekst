import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { defineStore } from 'pinia';
import { useStateStore, useLayersStore } from '@/stores';
import type { AnyLayerRead, AnyUnitRead, NodeRead } from '@/api';
import { GET } from '@/api';
import { pickTranslation } from '@/utils';
import { $t } from '@/i18n';
import { usePlatformData } from '@/platformData';
import { useMessages } from '@/messages';

export const useBrowseStore = defineStore('browse', () => {
  // composables
  const state = useStateStore();
  const layersStore = useLayersStore();
  const { pfData } = usePlatformData();
  const route = useRoute();
  const router = useRouter();
  const { message } = useMessages();

  /* BASIC BROWSE UI STATE */

  const showLayerToggleDrawer = ref(false);
  const reducedView = ref(false);
  const loadingNodePath = ref(true); // this is intentional!
  const loadingUnits = ref(false);
  const loading = computed(
    () => loadingUnits.value || loadingNodePath.value || layersStore.loading
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

  /* LAYERS AND UNITS */

  const layers = ref<AnyLayerRead[]>([]);
  const layersCount = computed(() => layers.value.length);
  const activeLayersCount = computed(() => layers.value.filter((l) => l.active).length);
  const layersCategorized = ref<
    { category: { key: string | undefined; translation: string }; layers: AnyLayerRead[] }[]
  >([]);

  watch(
    () => layersStore.data,
    (newLayers) => {
      // process changed available layers
      layers.value =
        newLayers.map((l) => {
          const existingLayer = layers.value.find((el) => l.id === el.id);
          return {
            ...l,
            active: !existingLayer || existingLayer.active,
            units: existingLayer?.units || [],
          };
        }) || [];
    }
  );

  watch(
    layers,
    () => {
      // compute categorized layers
      const categorized =
        pfData.value?.settings.layerCategories?.map((c) => ({
          category: { key: c.key, translation: pickTranslation(c.translations, state.locale) },
          layers: layers.value.filter((l) => l.category === c.key),
        })) || [];
      const uncategorized = [
        {
          category: {
            key: undefined,
            translation: $t('browse.uncategorized'),
          },
          layers: layers.value.filter(
            (l) => !categorized.find((c) => c.category.key === l.category)
          ),
        },
      ];
      layersCategorized.value = [...categorized, ...uncategorized].filter((c) => c.layers.length);
    },
    { immediate: true }
  );

  async function loadUnits(nodeIds: string[] = nodePath.value.map((n) => n.id)) {
    if (!nodeIds?.length || !state.text) {
      return;
    }
    loadingUnits.value = true;
    const { data, error } = await GET('/units', {
      params: { query: { nodeId: nodeIds } },
    });
    if (!error) {
      // assign units to layers
      layers.value.forEach((l: AnyLayerRead) => {
        l.units = data.filter((u: AnyUnitRead) => u.layerId == l.id);
      });
    } else {
      message.error('Error loading data layer units for this location', error.detail?.toString());
    }
    loadingUnits.value = false;
  }

  return {
    showLayerToggleDrawer,
    reducedView,
    loading,
    layersCount,
    activeLayersCount,
    layersCategorized,
    nodePath,
    nodePathHead,
    level,
    position,
    updateBrowseNodePath,
    resetBrowseLocation,
  };
});
