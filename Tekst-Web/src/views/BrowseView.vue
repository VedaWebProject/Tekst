<script setup lang="ts">
import LocationLabel from '@/components/browse/LocationLabel.vue';
import BrowseToolbar from '@/components/browse/BrowseToolbar.vue';
import { useBrowseStore } from '@/stores';
import LayerToggleDrawer from '@/components/browse/LayerToggleDrawer.vue';
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
import { computed } from 'vue';

const browse = useBrowseStore();
const { pfData } = usePlatformData();

const activeLayersCategorized = computed(() =>
  browse.layersCategorized
    .map((c) => ({
      ...c,
      layers: c.layers.filter(
        (l) =>
          l.active &&
          (l.level == browse.level || (l.config?.showOnParentLevel && l.level == browse.level + 1))
      ),
    }))
    .filter((c) => c.layers.length)
);
</script>

<template>
  <IconHeading level="1" :icon="MenuBookOutlined">
    <LocationLabel />&nbsp;
    <HelpButtonWidget help-key="browseView" />
  </IconHeading>

  <BrowseToolbar />

  <div
    v-if="activeLayersCategorized.length"
    class="unit-container-container"
    :class="browse.reducedView ? 'reduced' : ''"
  >
    <template v-for="category in activeLayersCategorized" :key="category.key">
      <h2
        v-if="
          pfData?.settings.showLayerCategoryHeadings &&
          activeLayersCategorized.length > 1 &&
          !browse.reducedView
        "
      >
        {{ category.category.translation }}
      </h2>
      <UnitContainer
        v-for="layer in category.layers"
        :key="layer.id"
        :loading="browse.loading"
        :layer="layer"
      />
    </template>
  </div>

  <HugeLabeledIcon
    v-else-if="browse.loading"
    :message="$t('init.loading')"
    :icon="HourglassTopTwotone"
  />

  <HugeLabeledIcon
    v-else-if="!browse.nodePath.length"
    :message="$t('browse.textNoNodes')"
    :icon="ErrorOutlineOutlined"
  />

  <HugeLabeledIcon v-else :message="$t('browse.locationNoData')" :icon="FolderOffTwotone" />

  <LayerToggleDrawer v-model:show="browse.showLayerToggleDrawer" />
</template>

<style scoped>
.browse-heading-location.smallscreen {
  font-size: 1.3rem;
}
.unit-container-container.reduced {
  box-shadow: var(--app-ui-block-box-shadow);
}
</style>
