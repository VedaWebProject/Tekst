<script setup lang="ts">
import { computed } from 'vue';
import { NDrawer, NDrawerContent } from 'naive-ui';
import { useAuthStore, useBrowseStore } from '@/stores';
import LayerToggleDrawerItem from '@/components/browse/LayerToggleDrawerItem.vue';
import IconHeading from '../typography/IconHeading.vue';

import LayersFilled from '@vicons/material/LayersFilled';

const props = defineProps<{ show: boolean }>();
const emits = defineEmits<{ (e: 'update:show', show: boolean): void }>();

const auth = useAuthStore();
const browse = useBrowseStore();

const show = computed({
  get() {
    return props.show;
  },
  set(value: boolean) {
    emits('update:show', value);
  },
});

function handleToggle(id: string, activate: boolean) {
  if (activate) {
    browse.activateLayer(id);
  } else {
    browse.deactivateLayer(id);
  }
}
</script>

<template>
  <n-drawer
    v-model:show="show"
    :width="680"
    :auto-focus="false"
    to="#app-container"
    style="max-width: 90%"
  >
    <n-drawer-content closable header-style="border: none">
      <template #header>
        <IconHeading level="2" :icon="LayersFilled" style="margin: 0">
          {{ $t('browse.layerToggleDrawer.heading') }}
        </IconHeading>
      </template>
      <template v-for="category in browse.layersCategorized" :key="category.category.key">
        <div v-if="browse.layersCategorized.length > 1" class="category-label">
          {{ category.category.translation }}
        </div>
        <LayerToggleDrawerItem
          v-for="layer in category.layers"
          :key="`${layer.id}`"
          :active="layer.active"
          :layer="layer"
          :user="auth.user"
          :disabled="!layer.units?.length"
          @update:active="(a) => handleToggle(layer.id, a)"
        />
      </template>
    </n-drawer-content>
  </n-drawer>
</template>

<style scoped>
.category-label {
  padding-bottom: 0.25rem;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid var(--main-bg-color);
}
</style>
