<script setup lang="ts">
import { computed } from 'vue';
import { NDrawer, NDrawerContent, NButton, NFlex, NIcon } from 'naive-ui';
import { useAuthStore, useBrowseStore, useResourcesStore, useThemeStore } from '@/stores';
import ResourceToggleDrawerItem from '@/components/browse/ResourceToggleDrawerItem.vue';
import IconHeading from '@/components/generic/IconHeading.vue';

import { CheckAllIcon, ResourceIcon, UncheckAllIcon } from '@/icons';
import LabelledSwitch from '@/components/LabelledSwitch.vue';

const show = defineModel<boolean>('show');

const auth = useAuthStore();
const browse = useBrowseStore();
const resources = useResourcesStore();
const theme = useThemeStore();

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
  <n-drawer v-model:show="show" :width="680" :auto-focus="false" style="max-width: 90%">
    <n-drawer-content closable header-style="border: none">
      <template #header>
        <icon-heading level="2" :icon="ResourceIcon" class="m-0">
          {{ $t('browse.resourceToggleDrawer.heading') }}
        </icon-heading>
      </template>

      <div
        v-if="auth.loggedIn && showNonPublicResourcesToggle"
        class="gray-box"
        :style="{ backgroundColor: theme.mainBgColor, marginTop: 0 }"
      >
        <labelled-switch
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
          :style="{ borderBottom: `1px solid ${theme.mainBgColor}` }"
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
  border: 10px solid var(--accent-color);
}

.category-header:first-child {
  margin-top: var(--gap-md);
}
</style>
