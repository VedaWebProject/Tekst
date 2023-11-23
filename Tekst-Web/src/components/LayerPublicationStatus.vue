<script setup lang="ts">
import type { AnyLayerRead } from '@/api';
import { NIcon } from 'naive-ui';
import { PublicFilled, FlagFilled, PublicOffFilled } from '@vicons/material';

defineProps<{
  layer: AnyLayerRead;
}>();
</script>

<template>
  <div style="font-size: var(--app-ui-font-size-small); font-style: italic">
    <div v-if="layer.public" class="layer-publication-status">
      <n-icon :component="PublicFilled" style="margin-right: 4px" />{{ $t('dataLayers.public') }}
    </div>
    <div v-else-if="layer.proposed" class="layer-publication-status">
      <n-icon :component="FlagFilled" style="margin-right: 4px" />{{ $t('dataLayers.proposed') }}
    </div>
    <div v-else class="layer-publication-status">
      <n-icon :component="PublicOffFilled" style="margin-right: 4px" />{{
        $t('dataLayers.notPublic')
      }}
    </div>
  </div>
</template>

<style scoped>
.layer-publication-status {
  display: flex;
  align-items: center;
}
</style>
