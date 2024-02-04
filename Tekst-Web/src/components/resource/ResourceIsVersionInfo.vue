<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import { NIcon } from 'naive-ui';
import { useResourcesStore } from '@/stores';

import { VersionIcon } from '@/icons';

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
    :style="size ? `font-size: var(--font-size-${size})` : ''"
  >
    <n-icon v-if="showIcon" :component="VersionIcon" />
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
