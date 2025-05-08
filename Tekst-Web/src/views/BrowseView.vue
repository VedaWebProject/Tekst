<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import LocationLabel from '@/components/LocationLabel.vue';
import BrowseToolbar from '@/components/browse/BrowseToolbar.vue';
import ContentContainer from '@/components/browse/ContentContainer.vue';
import ResourceToggleDrawer from '@/components/browse/ResourceToggleDrawer.vue';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { $t } from '@/i18n';
import { BookIcon, ErrorIcon, HourglassIcon, NoContentIcon } from '@/icons';
import { useAuthStore, useBrowseStore, useStateStore } from '@/stores';
import { NButton, NFlex, NTag } from 'naive-ui';
import { computed, onMounted, watch } from 'vue';

const props = defineProps<{
  textSlug?: string;
  locId?: string;
}>();

const auth = useAuthStore();
const browse = useBrowseStore();
const state = useStateStore();

const catHiddenResCount = computed<Record<string, number>>(() =>
  Object.fromEntries(
    browse.resourcesCategorized.map((c) => [
      c.category.key,
      c.resources.length - c.resources.filter((r) => r.active).length,
    ])
  )
);

function handleShowAllClick(categoryKey?: string) {
  if (!categoryKey) return;
  browse.setResourcesActiveState(
    browse.resourcesCategorized
      .find((c) => c.category.key === categoryKey)
      ?.resources.map((r) => r.id) || [],
    true
  );
}

// load fresh location data everytime the browse location changes in the URL
watch(
  () => props.locId,
  async (newLocId) => {
    await browse.loadLocationData(newLocId);
  }
);

watch(
  () => auth.user?.id,
  () => {
    browse.loadLocationData(props.locId, true);
  }
);

onMounted(() => {
  browse.loadLocationData(props.locId, true);
});
</script>

<template>
  <icon-heading v-if="!!browse.locationPath.length" level="1" :icon="BookIcon">
    <location-label />
    <help-button-widget help-key="browseView" />
  </icon-heading>

  <n-flex
    v-if="state.pf?.state.showLocationAliases && !!browse.locationPathHead?.aliases?.length"
    class="mb-lg"
    :title="$t('browse.location.aliasesTip')"
  >
    <n-tag v-for="alias in browse.locationPathHead?.aliases" :key="alias" size="small">
      {{ alias }}
    </n-tag>
  </n-flex>

  <browse-toolbar v-if="browse.locationPath.length" />

  <div
    v-if="browse.resourcesCategorized.length"
    class="content-blocks-wrapper"
    :class="{ 'focus-view': browse.focusView, 'box-shadow': browse.focusView }"
  >
    <template v-for="category in browse.resourcesCategorized" :key="category.category.key">
      <n-flex
        v-if="
          state.pf?.state.showResourceCategoryHeadings &&
          !!category.resources.length &&
          !browse.focusView &&
          !!category.category.translation
        "
        align="baseline"
        class="mb-md"
      >
        <h2
          class="mb-0"
          :class="{
            translucent:
              catHiddenResCount[category.category.key || ''] === category.resources.length,
          }"
        >
          {{ category.category.translation }}
        </h2>
        <n-button
          v-if="!!catHiddenResCount[category.category.key || '']"
          text
          :focusable="false"
          size="tiny"
          class="translucent"
          @click="() => handleShowAllClick(category.category.key)"
        >
          {{ $t('browse.showAllResources') }}
        </n-button>
      </n-flex>
      <content-container
        v-for="resource in category.resources"
        :key="resource.id"
        :loading="browse.loading"
        :resource="resource"
      />
    </template>
  </div>

  <huge-labelled-icon
    v-else-if="browse.loading"
    :message="$t('common.loading')"
    :icon="HourglassIcon"
  />

  <huge-labelled-icon
    v-else-if="!browse.locationPath.length"
    :message="$t('browse.textNoLocations')"
    :icon="ErrorIcon"
  />

  <huge-labelled-icon v-else :message="$t('browse.locationNoData')" :icon="NoContentIcon" />

  <resource-toggle-drawer v-model:show="browse.showResourceToggleDrawer" />
</template>

<style scoped>
.browse-heading-location.smallscreen {
  font-size: 1.3rem;
}

.content-blocks-wrapper {
  border-radius: var(--border-radius);
}
</style>
