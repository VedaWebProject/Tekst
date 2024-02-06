<script setup lang="ts">
import { computed } from 'vue';
import { NSwitch, NIcon, NSpace } from 'naive-ui';
import { $t } from '@/i18n';
import MetadataDisplayMinimal from '@/components/resource/MetadataDisplayMinimal.vue';
import { useStateStore } from '@/stores';
import type { AnyResourceRead, UserRead } from '@/api';

import { PublicIcon, ProposedIcon, UserIcon } from '@/icons';

const props = defineProps<{
  active?: boolean;
  resource: AnyResourceRead;
  disabled?: boolean;
  user?: UserRead;
}>();
const emit = defineEmits<{ (e: 'update:active', active: boolean): void }>();

const active = computed({
  get() {
    return props.active;
  },
  set(value: boolean) {
    emit('update:active', value);
  },
});

const state = useStateStore();
const infoTooltip = computed(() =>
  props.disabled ? $t('browse.locationResourceNoData') : undefined
);
</script>

<template>
  <n-space class="item" :class="disabled && 'disabled'" :title="infoTooltip" align="center">
    <n-switch v-model:value="active" :round="false" />
    <div class="item-main">
      <div class="item-title-container">
        <div class="item-title accent-color-text">{{ resource.title }}</div>
        <div class="item-title-extra">
          ({{ $t('browse.location.level') }}: {{ state.textLevelLabels[resource.level] }})
        </div>
      </div>
      <div class="item-meta">
        <metadata-display-minimal :data="resource.meta" :resource-type="resource.resourceType" />
      </div>
    </div>
    <div v-if="user" class="item-extra">
      <n-icon
        v-if="resource.ownerId === user.id"
        :component="UserIcon"
        :title="$t('resources.ownedByMe')"
      />
      <n-icon
        v-if="resource.public"
        :component="PublicIcon"
        :title="$t('models.resource.public')"
      />
      <n-icon
        v-else-if="resource.proposed"
        :component="ProposedIcon"
        :title="$t('models.resource.proposed')"
      />
    </div>
  </n-space>
</template>

<style scoped>
.item {
  margin-bottom: var(--layout-gap);
  padding-left: 0.5rem;
}

.item > .item-main {
  min-width: 1px;
  flex-grow: 2;
}

.item.disabled > .item-main {
  opacity: 0.5;
  cursor: help;
}

.item .item-title-container {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  column-gap: 12px;
}

.item .item-title-extra {
  opacity: 0.75;
  font-size: 0.8em;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item .item-meta {
  opacity: 0.75;
  font-size: var(--font-size-mini);
}

.item .item-title,
.item .item-meta {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-extra {
  display: flex;
  gap: 0.5rem;
  opacity: 0.5;
}
</style>
