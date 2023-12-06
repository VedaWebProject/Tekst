<script setup lang="ts">
import { computed } from 'vue';
import { NDrawer, NDrawerContent } from 'naive-ui';
import { useBrowseStore } from '@/stores';
import LayerToggleDrawerItem from '@/components/browse/LayerToggleDrawerItem.vue';

const props = defineProps<{ show: boolean }>();
const emits = defineEmits<{ (e: 'update:show', show: boolean): void }>();

const browse = useBrowseStore();

const show = computed({
  get() {
    return props.show;
  },
  set(value: boolean) {
    emits('update:show', value);
  },
});
</script>

<template>
  <n-drawer
    v-model:show="show"
    :width="600"
    :auto-focus="false"
    to="#app-container"
    style="max-width: 90%"
  >
    <n-drawer-content
      :title="$t('browse.layerToggleDrawer.heading')"
      header-style="font-size: var(--app-ui-font-size-huge); font-weight: var(--app-ui-font-weight-light)"
      closable
    >
      <LayerToggleDrawerItem
        v-for="layer in browse.layers"
        :key="`${layer.id}`"
        v-model:active="layer.active"
        :layer="layer"
        :disabled="!layer.units?.length"
      />
    </n-drawer-content>
  </n-drawer>
</template>
