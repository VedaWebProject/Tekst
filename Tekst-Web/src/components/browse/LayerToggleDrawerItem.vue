<script setup lang="ts">
import { computed } from 'vue';
import { NSwitch, NIcon } from 'naive-ui';
import CheckRound from '@vicons/material/CheckRound';
import { $t } from '@/i18n';
import MetadataDisplayMinimal from './MetadataDisplayMinimal.vue';
import { useStateStore } from '@/stores';

const props = defineProps<{
  active?: boolean;
  layer: Record<string, any>;
  disabled?: boolean;
}>();
const emits = defineEmits<{ (e: 'update:active', active: boolean): void }>();

const active = computed({
  get() {
    return props.active;
  },
  set(value: boolean) {
    emits('update:active', value);
  },
});

const state = useStateStore();
const infoTooltip = computed(() => (props.disabled ? $t('browse.locationLayerNoData') : undefined));
</script>

<template>
  <div class="layer-toggle-item" :class="disabled && 'disabled'" :title="infoTooltip">
    <n-switch v-model:value="active" size="large" :round="false">
      <template #checked-icon>
        <n-icon :component="CheckRound" />
      </template>
    </n-switch>
    <div class="layer-toggle-item-main">
      <div class="layer-toggle-item-title-container">
        <div class="layer-toggle-item-title">{{ layer.title }}</div>
        <div class="layer-toggle-item-title-extra">
          ({{ $t('browse.location.level') }}: {{ state.textLevelLabels[layer.level] }})
        </div>
      </div>
      <div class="layer-toggle-item-meta">
        <MetadataDisplayMinimal :data="layer.meta" :layer-type="layer.layerType" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.layer-toggle-item {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 24px;
  margin-bottom: 1rem;
}

.layer-toggle-item > .layer-toggle-item-main {
  min-width: 1px;
  flex-grow: 2;
}

.layer-toggle-item.disabled > .layer-toggle-item-main {
  opacity: 0.5;
  cursor: help;
}

.layer-toggle-item .layer-toggle-item-title-container {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  column-gap: 12px;
}

.layer-toggle-item .layer-toggle-item-title {
  color: var(--accent-color);
  font-size: var(--app-ui-font-size-medium);
  font-weight: var(--app-ui-font-weight-normal);
}

.layer-toggle-item .layer-toggle-item-title-extra {
  opacity: 0.75;
  font-size: 0.8em;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.layer-toggle-item .layer-toggle-item-meta {
  opacity: 0.75;
  font-size: var(--app-ui-font-size-mini);
  font-weight: var(--app-ui-font-weight-light);
}

.layer-toggle-item .layer-toggle-item-title,
.layer-toggle-item .layer-toggle-item-meta {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
