<script setup lang="ts">
import LocationLabel from '@/components/browse/LocationLabel.vue';
import BrowseToolbar from '@/components/browse/BrowseToolbar.vue';
import { useBrowseStore } from '@/stores';
import ResourceToggleDrawer from '@/components/browse/ResourceToggleDrawer.vue';
import UnitContainer from '@/components/browse/UnitContainer.vue';
import HugeLabeledIcon from '@/components/HugeLabeledIcon.vue';
import HelpButtonWidget from '@/components/widgets/HelpButtonWidget.vue';
import IconHeading from '@/components/typography/IconHeading.vue';

import FolderOffTwotone from '@vicons/material/FolderOffTwotone';
import HourglassTopTwotone from '@vicons/material/HourglassTopTwotone';
import MenuBookOutlined from '@vicons/material/MenuBookOutlined';
import ErrorOutlineOutlined from '@vicons/material/ErrorOutlineOutlined';
import { usePlatformData } from '@/platformData';
import { $t } from '@/i18n';
import { computed, onMounted } from 'vue';

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

onMounted(() => {
  browse.updateBrowseNodePath();
});
</script>

<template>
  <IconHeading level="1" :icon="MenuBookOutlined">
    <LocationLabel />
    <HelpButtonWidget help-key="browseView" />
  </IconHeading>

  <BrowseToolbar />

  <div
    v-if="activeResourcesCategorized.length"
    class="unit-container-container"
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
      <UnitContainer
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
.unit-container-container.reduced {
  box-shadow: var(--app-ui-block-box-shadow);
}
</style>
