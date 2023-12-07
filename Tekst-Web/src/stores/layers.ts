import { defineStore } from 'pinia';
import { computed, ref, watch } from 'vue';
import { GET, type AnyLayerRead, type AnyUnitRead } from '@/api';
import { useAuthStore, useStateStore } from '@/stores';
import { useMessages } from '@/messages';

export const useLayersStore = defineStore('layers', () => {
  const state = useStateStore();
  const auth = useAuthStore();
  const { message } = useMessages();

  const layers = ref<AnyLayerRead[]>([]);
  const error = ref(false);

  const loadingLayers = ref(false);
  const loadingUnits = ref(false);
  const loading = computed(() => loadingLayers.value || loadingUnits.value);

  async function loadLayers() {
    if (loadingLayers.value || !state.text) {
      return;
    }
    loadingLayers.value = true;
    layers.value = [];
    error.value = false;

    const { data, error: err } = await GET('/layers', {
      params: {
        query: {
          textId: state.text.id,
        },
      },
    });

    if (!err) {
      layers.value = data.map((l) => {
        const existingLayer = layers.value.find((lo) => lo.id === l.id);
        return {
          ...l,
          active: !existingLayer || existingLayer.active,
          units: existingLayer?.units || [],
        };
      });
      error.value = false;
    } else {
      error.value = true;
    }
    loadingLayers.value = false;
  }

  async function loadUnits(nodeIds: string[]) {
    if (loadingUnits.value || !state.text) {
      return;
    }
    loadingUnits.value = true;
    const { data: units, error } = await GET('/units', {
      params: { query: { nodeId: nodeIds } },
    });
    if (!error) {
      // assign units to layers
      layers.value.forEach((l: AnyLayerRead) => {
        l.units = units.filter((u: AnyUnitRead) => u.layerId == l.id);
      });
    } else {
      message.error('Error loading data layer units for this location', error.detail?.toString());
    }
    loadingUnits.value = false;
  }

  function replace(layer: AnyLayerRead) {
    layers.value = layers.value.map((l) =>
      l.id === layer.id ? { ...layer, active: l.active, units: l.units } : l
    );
  }

  // watch for events that trigger a reload of layers data
  watch(
    [() => auth.loggedIn, () => state.text],
    () => {
      loadLayers();
    },
    { immediate: true }
  );

  return {
    data: layers,
    error,
    loading,
    loadLayers,
    loadUnits,
    replace,
  };
});
