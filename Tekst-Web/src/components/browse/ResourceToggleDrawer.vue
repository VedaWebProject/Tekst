<script setup lang="ts">
import { computed } from 'vue';
import { NDrawer, NDrawerContent, NButton, NSpace, NIcon } from 'naive-ui';
import { useAuthStore, useBrowseStore } from '@/stores';
import ResourceToggleDrawerItem from '@/components/browse/ResourceToggleDrawerItem.vue';
import IconHeading from '@/components/generic/IconHeading.vue';

import { DeselectAllIcon, ResourceIcon, SelectAllIcon } from '@/icons';

const props = defineProps<{ show: boolean }>();
const emit = defineEmits<{ (e: 'update:show', show: boolean): void }>();

const auth = useAuthStore();
const browse = useBrowseStore();

const categoryActivationState = computed(() =>
  browse.resourcesCategorized.map((c) => c.resources.every((r) => r.active))
);

const show = computed({
  get() {
    return props.show;
  },
  set(value: boolean) {
    emit('update:show', value);
  },
});

function toggleCategory(index: number, activate: boolean) {
  browse.resourcesCategorized[index].resources.forEach((r) => {
    r.active = activate;
  });
}
</script>

<template>
  <n-drawer v-model:show="show" :width="680" :auto-focus="false" style="max-width: 90%">
    <n-drawer-content closable header-style="border: none">
      <template #header>
        <icon-heading level="2" :icon="ResourceIcon" style="margin: 0">
          {{ $t('browse.resourceToggleDrawer.heading') }}
        </icon-heading>
      </template>
      <template
        v-for="(category, index) in browse.resourcesCategorized"
        :key="category.category.key"
      >
        <n-space
          v-if="browse.resourcesCategorized.length > 1"
          class="category-header"
          align="center"
          justify="space-between"
        >
          <h3 style="margin: 0">{{ category.category.translation }}</h3>
          <n-button
            quaternary
            circle
            :focusable="false"
            @click="toggleCategory(index, !categoryActivationState[index])"
          >
            <template #icon>
              <n-icon
                :component="!categoryActivationState[index] ? SelectAllIcon : DeselectAllIcon"
              />
            </template>
          </n-button>
        </n-space>
        <resource-toggle-drawer-item
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
.category-header {
  padding-bottom: 0.5rem;
  margin: 1.5rem 0 var(--content-gap) 0;
  border-bottom: 1px solid var(--main-bg-color);
}

.category-header:first-child {
  margin-top: var(--content-gap);
}
</style>
