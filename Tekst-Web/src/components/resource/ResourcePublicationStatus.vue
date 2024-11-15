<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import { NFlex, NIcon } from 'naive-ui';

import { ProposedIcon, PublicIcon, PublicOffIcon } from '@/icons';

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
  <n-flex align="center" size="small" :style="size ? `font-size: var(--font-size-${size})` : ''">
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
  </n-flex>
</template>
