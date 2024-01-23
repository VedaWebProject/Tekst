<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import { NIcon } from 'naive-ui';

import { PublicIcon, ProposedIcon, PublicOffIcon } from '@/icons';

withDefaults(
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
</script>

<template>
  <div
    class="resource-publication-status"
    :style="size ? `font-size: var(--app-ui-font-size-${size})` : ''"
  >
    <template v-if="resource.public">
      <n-icon v-if="showIcon" :component="PublicIcon" />
      {{ $t('resources.public') }}
    </template>
    <template v-else-if="resource.proposed">
      <n-icon v-if="showIcon" :component="ProposedIcon" />
      {{ $t('resources.proposed') }}
    </template>
    <template v-else>
      <n-icon v-if="showIcon" :component="PublicOffIcon" />
      {{ $t('resources.notPublic') }}
    </template>
  </div>
</template>

<style scoped>
.resource-publication-status {
  display: flex;
  align-items: center;
}
.resource-publication-status > .n-icon {
  margin-right: 0.25rem;
}
</style>
