<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import { NIcon, NFlex } from 'naive-ui';
import { useResourcesStore, useStateStore } from '@/stores';

import { VersionIcon } from '@/icons';
import { pickTranslation } from '@/utils';

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

const state = useStateStore();

const resources = useResourcesStore();
const originalTitle = pickTranslation(
  resources.ofText.find((r) => r.id == props.resource.originalId)?.title,
  state.locale
);
</script>

<template>
  <n-flex
    v-if="resource.originalId"
    align="center"
    size="small"
    :style="size ? `font-size: var(--font-size-${size})` : ''"
  >
    <n-icon v-if="showIcon" :component="VersionIcon" />
    {{ $t('resources.versionOf', { title: originalTitle || $t('resources.unknownOriginal') }) }}
  </n-flex>
</template>
>
