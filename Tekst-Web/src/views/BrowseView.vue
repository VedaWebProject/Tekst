<script setup lang="ts">
import LocationLabel from '@/components/LocationLabel.vue';
import BrowseToolbar from '@/components/browse/BrowseToolbar.vue';
import { useAuthStore, useBrowseStore } from '@/stores';
import ResourceToggleDrawer from '@/components/browse/ResourceToggleDrawer.vue';
import ContentContainer from '@/components/browse/ContentContainer.vue';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { usePlatformData } from '@/composables/platformData';
import { $t } from '@/i18n';
import { computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';

import { NoContentIcon, HourglassIcon, BookIcon, ErrorIcon } from '@/icons';

const auth = useAuthStore();
const route = useRoute();
const browse = useBrowseStore();
const { pfData } = usePlatformData();

const activeResourcesCategorized = computed(() =>
  browse.resourcesCategorized
    .map((c) => ({
      ...c,
      resources: c.resources.filter(
        (r) =>
          r.active &&
          (r.level <= browse.level ||
            (r.config?.common?.showOnParentLevel && r.level == browse.level + 1))
      ),
    }))
    .filter((c) => c.resources.length)
);

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
  <icon-heading v-if="browse.locationPath.length" level="1" :icon="BookIcon">
    <location-label />
    <help-button-widget help-key="browseView" />
  </icon-heading>

  <browse-toolbar v-if="browse.locationPath.length" />

  <div
    v-if="activeResourcesCategorized.length"
    class="content-container-container"
    :class="browse.reducedView ? 'reduced' : ''"
  >
    <template v-for="category in activeResourcesCategorized" :key="category.key">
      <h2
        v-if="
          pfData?.settings.showResourceCategoryHeadings &&
          (activeResourcesCategorized.length > 1 ||
            pfData?.settings.alwaysShowResourceCategoryHeadings) &&
          !browse.reducedView
        "
      >
        {{ category.category.translation }}
      </h2>
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
