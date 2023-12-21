<script setup lang="ts">
import { computed } from 'vue';
import { NSwitch, NIcon } from 'naive-ui';
import { $t } from '@/i18n';
import MetadataDisplayMinimal from '@/components/browse/MetadataDisplayMinimal.vue';
import { useStateStore } from '@/stores';
import type { AnyResourceRead, UserRead } from '@/api';

import PublicFilled from '@vicons/material/PublicFilled';
import FlagFilled from '@vicons/material/FlagFilled';
import PersonFilled from '@vicons/material/PersonFilled';

const props = defineProps<{
  active?: boolean;
  resource: AnyResourceRead;
  disabled?: boolean;
  user?: UserRead;
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
const infoTooltip = computed(() =>
  props.disabled ? $t('browse.locationResourceNoData') : undefined
);
</script>

<template>
  <div class="item" :class="disabled && 'disabled'" :title="infoTooltip">
    <n-switch v-model:value="active" size="large" :round="false" />
    <div class="item-main">
      <div class="item-title-container">
        <div class="item-title">{{ resource.title }}</div>
        <div class="item-title-extra">
          ({{ $t('browse.location.level') }}: {{ state.textLevelLabels[resource.level] }})
        </div>
      </div>
      <div class="item-meta">
        <MetadataDisplayMinimal :data="resource.meta" :resource-type="resource.resourceType" />
      </div>
    </div>
    <div v-if="user" class="item-extra">
      <n-icon
        v-if="resource.ownerId === user.id"
        :component="PersonFilled"
        :title="$t('resources.ownedByMe')"
      />
      <n-icon
        v-if="resource.public"
        :component="PublicFilled"
        :title="$t('models.resource.public')"
      />
      <n-icon
        v-else-if="resource.proposed"
        :component="FlagFilled"
        :title="$t('models.resource.proposed')"
      />
    </div>
  </div>
</template>

<style scoped>
.item {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 24px;
  margin-bottom: 1rem;
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

.item .item-title {
  color: var(--accent-color);
  font-size: var(--app-ui-font-size-medium);
  font-weight: var(--app-ui-font-weight-normal);
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
  font-size: var(--app-ui-font-size-mini);
  font-weight: var(--app-ui-font-weight-light);
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