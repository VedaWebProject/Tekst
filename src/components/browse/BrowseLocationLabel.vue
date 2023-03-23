<script setup lang="ts">
import { ref, watch } from 'vue';
import { useStateStore, useBrowseStore } from '@/stores';

const state = useStateStore();
const browse = useBrowseStore();

const browseLocationLabel = ref();

// update browse location label as node path changes
watch(
  () => browse.nodePath,
  (after) =>
    (browseLocationLabel.value = after
      .map((n, i) => {
        const lvlLabel = state.text?.levels[i];
        const nodePrefix = state.text?.labeledLevels && lvlLabel ? `${lvlLabel}: ` : '';
        return n.label ? `${nodePrefix}${n.label}` : '';
      })
      .join(state.text?.locDelim || ', '))
);
</script>

<template>
  <span>{{ browseLocationLabel }}</span>
</template>
