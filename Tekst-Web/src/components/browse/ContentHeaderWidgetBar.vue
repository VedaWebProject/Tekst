<script setup lang="ts">
import type { StyleValue } from 'vue';
import contentWidgets from '@/components/content/mappings';
import LocationContentSiblingsWidget from '@/components/resource/LocationContentSiblingsWidget.vue';
import ResourceInfoWidget from '@/components/resource/ResourceInfoWidget.vue';
import ResourceDeactivateWidget from '@/components/resource/ResourceDeactivateWidget.vue';
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
  <div class="content-header-widgets" :style="style">
    <!-- config-specific widgets -->
    <template v-if="resource.contents?.length">
      <template
        v-for="(configSection, configSectionKey) in resource.config"
        :key="configSectionKey"
      >
        <component
          :is="contentWidgets[configSectionKey]"
          v-if="configSectionKey in contentWidgets"
          :resource="resource"
          :widget-config="configSection"
        />
      </template>
    </template>
    <!-- generic content widgets -->
    <LocationContentSiblingsWidget
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
.content-header-widgets {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  gap: 8px;
  transition: opacity 0.2s ease;
}
</style>
