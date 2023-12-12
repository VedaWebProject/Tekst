import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import { GET, type AnyLayerRead } from '@/api';
import { useAuthStore, useStateStore } from '@/stores';

export const useLayersStore = defineStore('layers', () => {
  const state = useStateStore();
  const auth = useAuthStore();

  const layers = ref<AnyLayerRead[]>([]);
  const error = ref(false);

  const loading = ref(false);

  async function load() {
    if (loading.value || !state.text) {
      return;
    }
    loading.value = true;
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
    loading.value = false;
  }

  function replace(layer: AnyLayerRead) {
    layers.value = layers.value.map((l) => (l.id === layer.id ? layer : l));
  }

  function add(layer: AnyLayerRead) {
    layers.value = layers.value.concat([layer]);
  }

  // watch for events that trigger a reload of layers data
  watch(
    [() => auth.loggedIn, () => state.text],
    () => {
      load();
    },
    { immediate: true }
  );

  return {
    data: layers,
    error,
    loading,
    load,
    replace,
    add,
  };
});
