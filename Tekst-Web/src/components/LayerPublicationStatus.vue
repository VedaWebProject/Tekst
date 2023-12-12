<script setup lang="ts">
import type { AnyLayerRead } from '@/api';
import { NIcon } from 'naive-ui';
import { PublicFilled, FlagFilled, PublicOffFilled } from '@vicons/material';

withDefaults(
  defineProps<{
    layer: AnyLayerRead;
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
    class="layer-publication-status"
    :style="size ? `font-size: var(--app-ui-font-size-${size})` : ''"
  >
    <template v-if="layer.public">
      <n-icon v-if="showIcon" :component="PublicFilled" />
      {{ $t('dataLayers.public') }}
    </template>
    <template v-else-if="layer.proposed">
      <n-icon v-if="showIcon" :component="FlagFilled" />
      {{ $t('dataLayers.proposed') }}
    </template>
    <template v-else>
      <n-icon v-if="showIcon" :component="PublicOffFilled" />
      {{ $t('dataLayers.notPublic') }}
    </template>
  </div>
</template>

<style scoped>
.layer-publication-status {
  display: flex;
  align-items: center;
}
.layer-publication-status > .n-icon {
  margin-right: 0.25rem;
}
</style>
