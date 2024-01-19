<script setup lang="ts">
import LocationLabel from '@/components/browse/LocationLabel.vue';
import BrowseToolbar from '@/components/browse/BrowseToolbar.vue';
import { useAuthStore, useBrowseStore } from '@/stores';
import ResourceToggleDrawer from '@/components/browse/ResourceToggleDrawer.vue';
import ContentContainer from '@/components/browse/ContentContainer.vue';
import HugeLabeledIcon from '@/components/HugeLabeledIcon.vue';
import HelpButtonWidget from '@/components/widgets/HelpButtonWidget.vue';
import IconHeading from '@/components/typography/IconHeading.vue';
import { usePlatformData } from '@/platformData';
import { $t } from '@/i18n';
import { computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';

import FolderOffTwotone from '@vicons/material/FolderOffTwotone';
import HourglassTopTwotone from '@vicons/material/HourglassTopTwotone';
import MenuBookOutlined from '@vicons/material/MenuBookOutlined';
import ErrorOutlineOutlined from '@vicons/material/ErrorOutlineOutlined';

const auth = useAuthStore();
const route = useRoute();
const browse = useBrowseStore();
const { pfData } = usePlatformData();

const activeResourcesCategorized = computed(() =>
  browse.resourcesCategorized
    .map((c) => ({
      ...c,
      resources: c.resources.filter(
        (l) =>
          l.active &&
          (l.level <= browse.level || (l.config?.showOnParentLevel && l.level == browse.level + 1))
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
  <IconHeading v-if="browse.nodePath.length" level="1" :icon="MenuBookOutlined">
    <LocationLabel />
    <HelpButtonWidget help-key="browseView" />
  </IconHeading>

  <BrowseToolbar v-if="browse.nodePath.length" />

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
      <ContentContainer
        v-for="resource in category.resources"
        :key="resource.id"
        :loading="browse.loading"
        :resource="resource"
      />
    </template>
  </div>

  <HugeLabeledIcon
    v-else-if="browse.loading"
    :message="$t('general.loading')"
    :icon="HourglassTopTwotone"
  />

  <HugeLabeledIcon
    v-else-if="!browse.nodePath.length"
    :message="$t('browse.textNoNodes')"
    :icon="ErrorOutlineOutlined"
  />

  <HugeLabeledIcon v-else :message="$t('browse.locationNoData')" :icon="FolderOffTwotone" />

  <ResourceToggleDrawer v-model:show="browse.showResourceToggleDrawer" />
</template>

<style scoped>
.browse-heading-location.smallscreen {
  font-size: 1.3rem;
}
.content-container-container.reduced {
  box-shadow: var(--app-ui-block-box-shadow);
}
</style>
