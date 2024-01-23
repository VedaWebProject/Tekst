<script setup lang="ts">
import { computed } from 'vue';
import { NDrawer, NDrawerContent } from 'naive-ui';
import { useAuthStore, useBrowseStore } from '@/stores';
import ResourceToggleDrawerItem from '@/components/browse/ResourceToggleDrawerItem.vue';
import IconHeading from '@/components/generic/IconHeading.vue';

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
          {{ $t('browse.resourceToggleDrawer.heading') }}
        </IconHeading>
      </template>
      <template v-for="category in browse.resourcesCategorized" :key="category.category.key">
        <div v-if="browse.resourcesCategorized.length > 1" class="category-label">
          {{ category.category.translation }}
        </div>
        <ResourceToggleDrawerItem
          v-for="resource in category.resources"
          :key="`${resource.id}`"
          v-model:active="resource.active"
          :resource="resource"
          :user="auth.user"
          :disabled="!resource.contents?.length"
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
