<script setup lang="ts">
import type { CSSProperties } from 'vue';
import unitWidgets from '@/components/browse/widgets/mappings';
import UnitSiblingsWidget from './widgets/UnitSiblingsWidget.vue';
import LayerInfoWidget from './widgets/LayerInfoWidget.vue';
import LayerDeactivateWidget from './widgets/LayerDeactivateWidget.vue';
import { useBrowseStore } from '@/stores';

interface Props {
  layer: Record<string, any>;
  style?: CSSProperties;
  showMergeWidget?: boolean;
  showDeactivateWidget?: boolean;
}

withDefaults(defineProps<Props>(), {
  showDeactivateWidget: true,
  showMergeWidget: true,
});

const browse = useBrowseStore();
</script>

<template>
  <div class="unit-header-widgets" :style="style">
    <!-- config-specific widgets -->
    <template v-if="layer.units.length">
      <template v-for="(configSection, configSectionKey) in layer.config" :key="configSectionKey">
        <component
          v-if="configSectionKey in unitWidgets"
          :is="unitWidgets[configSectionKey]"
          :layer="layer"
          :widget-config="configSection"
        />
      </template>
    </template>
    <!-- generic unit widgets -->
    <UnitSiblingsWidget
      v-if="(showMergeWidget ?? true) && browse.level >= layer.level - 1"
      :layer="layer"
    />
    <LayerInfoWidget :layer="layer" />
    <LayerDeactivateWidget v-if="showDeactivateWidget ?? true" :layer="layer" />
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
