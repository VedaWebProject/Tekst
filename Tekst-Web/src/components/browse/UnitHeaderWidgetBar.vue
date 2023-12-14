<script setup lang="ts">
import type { StyleValue } from 'vue';
import unitWidgets from '@/components/browse/widgets/mappings';
import UnitSiblingsWidget from './widgets/UnitSiblingsWidget.vue';
import ResourceInfoWidget from './widgets/ResourceInfoWidget.vue';
import ResourceDeactivateWidget from './widgets/ResourceDeactivateWidget.vue';
import { useBrowseStore } from '@/stores';
import type { AnyResourceRead } from '@/api';

interface Props {
  resource: AnyResourceRead;
  style?: StyleValue;
  showDeactivateWidget?: boolean;
  showSiblingsWidget?: boolean;
}

withDefaults(defineProps<Props>(), {
  showDeactivateWidget: true,
  showSiblingsWidget: true,
  style: undefined,
});

const browse = useBrowseStore();
</script>

<template>
  <div class="unit-header-widgets" :style="style">
    <!-- config-specific widgets -->
    <template v-if="resource.units?.length">
      <template
        v-for="(configSection, configSectionKey) in resource.config"
        :key="configSectionKey"
      >
        <component
          :is="unitWidgets[configSectionKey]"
          v-if="configSectionKey in unitWidgets"
          :resource="resource"
          :widget-config="configSection"
        />
      </template>
    </template>
    <!-- generic unit widgets -->
    <UnitSiblingsWidget
      v-if="
        showSiblingsWidget &&
        resource.config?.showOnParentLevel &&
        (browse.level == resource.level || browse.level == resource.level - 1)
      "
      :resource="resource"
    />
    <ResourceInfoWidget :resource="resource" />
    <ResourceDeactivateWidget v-if="showDeactivateWidget ?? true" :resource="resource" />
  </div>
</template>

<style scoped>
.unit-header-widgets {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  gap: 8px;
  transition: opacity 0.2s ease;
}
</style>
