<script setup lang="ts">
import type { StyleValue } from 'vue';
import contentWidgets from '@/components/content/mappings';
import LocationContentSiblingsWidget from '@/components/resource/LocationContentSiblingsWidget.vue';
import ResourceInfoWidget from '@/components/resource/ResourceInfoWidget.vue';
import ResourceDeactivateWidget from '@/components/resource/ResourceDeactivateWidget.vue';
import { useBrowseStore } from '@/stores';
import type { AnyResourceRead } from '@/api';
import ContentCommentWidget from '../resource/ContentCommentWidget.vue';

withDefaults(
  defineProps<{
    resource: AnyResourceRead;
    style?: StyleValue;
  }>(),
  {
    style: undefined,
  }
);

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
    <location-content-siblings-widget
      v-if="
        resource.config?.common?.showOnParentLevel &&
        (browse.level == resource.level || browse.level == resource.level - 1)
      "
      :resource="resource"
    />
    <content-comment-widget :resource="resource" />
    <resource-info-widget :resource="resource" />
    <resource-deactivate-widget :resource="resource" />
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
