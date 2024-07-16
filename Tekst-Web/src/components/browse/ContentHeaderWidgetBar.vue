<script setup lang="ts">
import type { StyleValue } from 'vue';
import contentWidgets from '@/components/resource/mappings';
import LocationContentSiblingsWidget from '@/components/resource/LocationContentSiblingsWidget.vue';
import ResourceInfoWidget from '@/components/resource/ResourceInfoWidget.vue';
import ResourceDeactivateWidget from '@/components/resource/ResourceDeactivateWidget.vue';
import type { AnyResourceRead } from '@/api';
import ContentCommentWidget from '@/components/resource/ContentCommentWidget.vue';
import ContentEditWidget from '@/components/resource/ContentEditWidget.vue';
import ResourceExportWidget from '@/components/resource/ResourceExportWidget.vue';
import CorrectionNoteWidget from '@/components/resource/CorrectionNoteWidget.vue';
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    resource: AnyResourceRead;
    style?: StyleValue;
    smallScreen?: boolean;
    reduced?: boolean;
  }>(),
  {
    style: undefined,
  }
);

const small = computed(() => props.reduced || props.smallScreen);
</script>

<template>
  <div class="content-header-widgets" :style="style">
    <!-- resource-type-specific widgets -->
    <template v-if="resource.contents?.length">
      <template
        v-for="(configSection, configSectionKey) in resource.config"
        :key="configSectionKey"
      >
        <component
          :is="contentWidgets[configSectionKey]"
          v-if="configSectionKey in contentWidgets"
          :widget-config="configSection"
          :resource="resource"
          :small="small"
        />
      </template>
    </template>
    <!-- generic content widgets -->
    <location-content-siblings-widget :resource="resource" :small="small" />
    <content-comment-widget :resource="resource" :small="small" />
    <content-edit-widget :resource="resource" :small="small" />
    <correction-note-widget :resource="resource" :small="small" />
    <resource-export-widget :resource="resource" :small="small" />
    <resource-info-widget :resource="resource" :small="small" />
    <resource-deactivate-widget :resource="resource" :small="small" />
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
