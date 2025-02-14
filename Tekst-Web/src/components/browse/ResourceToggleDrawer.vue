<script setup lang="ts">
import ResourceToggleDrawerItem from '@/components/browse/ResourceToggleDrawerItem.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { useAuthStore, useBrowseStore, useResourcesStore } from '@/stores';
import { NButton, NDrawer, NDrawerContent, NFlex, NIcon } from 'naive-ui';
import { computed } from 'vue';

import LabeledSwitch from '@/components/LabeledSwitch.vue';
import { CheckAllIcon, ResourceIcon, UncheckAllIcon } from '@/icons';

const show = defineModel<boolean>('show');

const auth = useAuthStore();
const browse = useBrowseStore();
const resources = useResourcesStore();

const showNonPublicResourcesToggle = computed(
  () => !!resources.ofText.filter((r) => !r.public).length
);
const categoryActivationState = computed(() =>
  browse.resourcesCategorized.map((c) => c.resources.every((r) => r.active))
);

function toggleCategory(index: number, activate: boolean) {
  browse.setResourcesActiveState(
    browse.resourcesCategorized[index].resources.map((r) => r.id),
    activate
  );
}
</script>

<template>
  <n-drawer v-model:show="show" :width="680" style="max-width: 90%">
    <n-drawer-content closable header-style="border: none">
      <template #header>
        <icon-heading level="2" :icon="ResourceIcon" class="m-0">
          {{ $t('browse.resourceToggleDrawer.heading') }}
        </icon-heading>
      </template>

      <div
        v-if="auth.loggedIn && showNonPublicResourcesToggle"
        class="gray-box"
        style="margin-top: 0"
      >
        <labeled-switch
          v-model="browse.showNonPublicResources"
          :label="$t('browse.resourceToggleDrawer.showNonPublicResources')"
          size="small"
        />
      </div>

      <template
        v-for="(category, index) in browse.resourcesCategorized"
        :key="category.category.key"
      >
        <n-flex
          v-if="browse.resourcesCategorized.length > 1"
          class="category-header"
          align="center"
          justify="space-between"
        >
          <h3 class="m-0">
            {{ category.category.translation }}
          </h3>
          <n-button
            quaternary
            circle
            size="small"
            :focusable="false"
            :title="
              categoryActivationState[index]
                ? $t('browse.resourceToggleDrawer.deactivateCategory')
                : $t('browse.resourceToggleDrawer.activateCategory')
            "
            @click="toggleCategory(index, !categoryActivationState[index])"
          >
            <template #icon>
              <n-icon
                :component="!categoryActivationState[index] ? CheckAllIcon : UncheckAllIcon"
              />
            </template>
          </n-button>
        </n-flex>
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
  margin: 1.5rem 0 0.8rem;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid var(--main-bg-color);
}

.category-header:first-child {
  margin-top: var(--gap-md);
}
</style>
