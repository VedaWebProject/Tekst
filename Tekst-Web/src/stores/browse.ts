import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { defineStore } from 'pinia';
import { useStateStore, useAuthStore } from '@/stores';
import type { AnyLayerRead, NodeRead } from '@/api';
import { GET } from '@/api';
import { useMessages } from '@/messages';

export const useBrowseStore = defineStore('browse', () => {
  // composables
  const state = useStateStore();
  const auth = useAuthStore();
  const route = useRoute();
  const router = useRouter();
  const { message } = useMessages();

  /* BASIC BROWSE UI STATE */

  const showLayerToggleDrawer = ref(false);
  const reducedView = ref(false);
  const loading = ref(true); // this is intentional!

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
    loading.value = true;
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
    loading.value = false;
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

  /* BROWSE LAYERS AND UNITS */

  const layers = ref<AnyLayerRead[]>([]);

  async function loadLayersData() {
    if (!state.text) return;
    // set to loading
    loading.value = true;
    // fetch layers data
    const { data: layersData, error } = await GET('/layers', {
      params: { query: { textId: state.text.id, owners: true } },
    });
    if (!error) {
      layersData.forEach((l: Record<string, any>) => {
        // keep layer deactivated if it was before
        const existingLayer = layers.value.find((lo) => lo.id === l.id);
        l.active = !existingLayer || existingLayer.active;
      });
      await loadUnitsData(layersData as AnyLayerRead[]);
    } else {
      message.error('Error loading data layers for this location', error.detail?.toString());
    }
    loading.value = false;
  }

  async function loadUnitsData(layersData: AnyLayerRead[] = layers.value) {
    if (!nodePathHead.value) {
      layers.value = [];
      return;
    }
    // set to loading
    loading.value = true;
    // fetch units data
    const { data: unitsData, error } = await GET('/units/', {
      params: { query: { nodeId: nodePath.value.map((n) => n.id) } },
    });
    if (!error) {
      // assign units to layers
      layersData.forEach((l: Record<string, any>) => {
        l.units = unitsData.filter((u: Record<string, any>) => u.layerId == l.id);
      });
      // assign (potentially) fresh layers/untis data to store prop
      layers.value = layersData;
    } else {
      message.error('Error loading data layer units for this location', error.detail?.toString());
    }
    loading.value = false;
  }

  // load layers/units data on browse location change
  watch(
    () => nodePathHead.value,
    (after: NodeRead | undefined, before: NodeRead | undefined) => {
      if (after?.textId === before?.textId && layers.value.length > 0) {
        // selected text didn't change, only the location did,
        // so it's enough to load new units data (secial case: if the layers
        // array is empty, we try to load layers again,
        // as the user might have just logged out)
        loadUnitsData();
      } else {
        // node path head changed because a different text was selected,
        // so we have to load full layers data AND according units data
        loadLayersData();
      }
    }
  );

  // remove accessed data that might be restricted
  watch(
    () => auth.user,
    (after, before) => {
      if (before && !after) layers.value = [];
    }
  );

  return {
    showLayerToggleDrawer,
    reducedView,
    loading,
    layers,
    nodePath,
    nodePathHead,
    nodePathRoot,
    level,
    position,
    updateBrowseNodePath,
    resetBrowseLocation,
    loadLayersData,
  };
});
