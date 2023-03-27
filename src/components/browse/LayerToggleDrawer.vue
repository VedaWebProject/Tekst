<script setup lang="ts">
import { computed } from 'vue';
import { NDrawer, NDrawerContent } from 'naive-ui';
import { useBrowseStore } from '@/stores';
import LayerToggleDrawerItem from '@/components/browse/LayerToggleDrawerItem.vue';

const browse = useBrowseStore();

const props = defineProps<{ show: boolean }>();
const emits = defineEmits<{ (e: 'update:show', show: boolean): void }>();

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
  <n-drawer v-model:show="show" :width="512" :auto-focus="false" style="max-width: 90%">
    <n-drawer-content title="Toggle Data Layers" :native-scrollbar="false" closable>
      <LayerToggleDrawerItem
        v-for="layer in browse.layers"
        v-model:active="layer.active"
        :key="layer.id"
        :title="layer.title"
        :layerType="layer.layerType"
      />
    </n-drawer-content>
  </n-drawer>
</template>
