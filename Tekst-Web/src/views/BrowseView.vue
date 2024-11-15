<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import LocationLabel from '@/components/LocationLabel.vue';
import BrowseToolbar from '@/components/browse/BrowseToolbar.vue';
import ContentContainer from '@/components/browse/ContentContainer.vue';
import ResourceToggleDrawer from '@/components/browse/ResourceToggleDrawer.vue';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { usePlatformData } from '@/composables/platformData';
import { $t } from '@/i18n';
import { BookIcon, ErrorIcon, HourglassIcon, NoContentIcon } from '@/icons';
import { useAuthStore, useBrowseStore, useSearchStore, useThemeStore } from '@/stores';
import { NButton, NFlex, NTag } from 'naive-ui';
import { computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';

const auth = useAuthStore();
const theme = useThemeStore();
const route = useRoute();
const browse = useBrowseStore();
const search = useSearchStore();
const { pfData } = usePlatformData();

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
  [() => route.query.lvl, () => route.query.pos],
  async ([newLvl, newPos]) => {
    await browse.loadLocationData(newLvl?.toString(), newPos?.toString());
  },
  { immediate: true }
);

watch(
  () => auth.loggedIn,
  () => {
    browse.loadLocationData(undefined, undefined, true);
  }
);

onMounted(() => {
  browse.loadLocationData(undefined, undefined, true);
});
</script>

<template>
  <icon-heading v-if="!!browse.locationPath.length" level="1" :icon="BookIcon">
    <location-label />
    <help-button-widget help-key="browseView" />
  </icon-heading>

  <n-flex
    v-if="pfData?.state.showLocationAliases && !!browse.locationPathHead?.aliases?.length"
    class="mb-lg"
    :title="$t('browse.location.aliasesTip')"
  >
    <n-tag
      v-for="alias in browse.locationPathHead?.aliases"
      :key="alias"
      size="small"
      :bordered="false"
      class="translucent"
      :color="{
        color: 'var(--main-bg-color)',
        textColor: 'var(--text-color)',
        borderColor: theme.accentColors.base,
      }"
    >
      {{ alias }}
    </n-tag>
  </n-flex>

  <browse-toolbar v-if="browse.locationPath.length" />

  <div
    v-if="browse.resourcesCategorized.length"
    class="content-container-container"
    :class="browse.reducedView ? 'reduced' : ''"
  >
    <template v-for="category in browse.resourcesCategorized" :key="category.category.key">
      <n-flex
        v-if="
          pfData?.state.showResourceCategoryHeadings &&
          !!category.resources.length &&
          !browse.reducedView &&
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
        :loading="browse.loading || search.loading"
        :resource="resource"
      />
    </template>
  </div>

  <huge-labelled-icon
    v-else-if="browse.loading"
    :message="$t('general.loading')"
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

.content-container-container.reduced {
  box-shadow: var(--block-box-shadow);
}
</style>
