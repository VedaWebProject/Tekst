<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import { NIcon } from 'naive-ui';

import AltRouteOutlined from '@vicons/material/AltRouteOutlined';
import { useResourcesStore } from '@/stores';

const props = withDefaults(
  defineProps<{
    resource: AnyResourceRead;
    showIcon?: boolean;
    size?: 'large' | 'medium' | 'small' | 'tiny' | 'mini';
  }>(),
  {
    showIcon: true,
    size: undefined,
  }
);

const resources = useResourcesStore();
const originalTitle = resources.data.find((r) => r.id == props.resource.originalId)?.title;
</script>

<template>
  <div
    v-if="resource.originalId"
    class="resource-is-version-info"
    :style="size ? `font-size: var(--app-ui-font-size-${size})` : ''"
  >
    <n-icon v-if="showIcon" :component="AltRouteOutlined" />
    {{ $t('resources.versionOf', { title: originalTitle || $t('resources.unknownOriginal') }) }}
  </div>
</template>

<style scoped>
.resource-is-version-info {
  display: flex;
  align-items: center;
}
.resource-is-version-info > .n-icon {
  margin-right: 0.25rem;
}
</style>
