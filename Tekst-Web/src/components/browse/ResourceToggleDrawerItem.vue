<script setup lang="ts">
import { computed } from 'vue';
import { NFlex, NSwitch, NIcon } from 'naive-ui';
import { $t } from '@/i18n';
import MetadataDisplayMinimal from '@/components/resource/MetadataDisplayMinimal.vue';
import { useStateStore } from '@/stores';
import type { AnyResourceRead, UserRead } from '@/api';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import { PublicIcon, ProposedIcon, PublicOffIcon } from '@/icons';

const props = defineProps<{
  resource: AnyResourceRead;
  disabled?: boolean;
  user?: UserRead;
}>();

const active = defineModel<boolean>('active');

const state = useStateStore();
const infoTooltip = computed(() =>
  props.disabled ? $t('browse.locationResourceNoData') : undefined
);
</script>

<template>
  <div class="item" :class="disabled && 'disabled'" :title="infoTooltip">
    <n-switch v-model:value="active" :round="false" />
    <div class="item-main">
      <n-flex align="baseline">
        <div class="item-title text-color-accent">
          <translation-display v-if="resource.title" :value="resource.title" />
        </div>
        <div class="item-title-extra">
          ({{ $t('browse.location.level') }}: {{ state.textLevelLabels[resource.level] }})
        </div>
      </n-flex>
      <div class="text-mini translucent ellipsis">
        <metadata-display-minimal :data="resource.meta" :resource-type="resource.resourceType" />
      </div>
    </div>
    <div v-if="user" class="item-extra">
      <n-icon v-if="resource.public" :component="PublicIcon" :title="$t('resources.public')" />
      <n-icon
        v-else-if="resource.proposed"
        :component="ProposedIcon"
        :title="$t('resources.proposed')"
      />
      <n-icon v-else :component="PublicOffIcon" :title="$t('resources.notPublic')" />
    </div>
  </div>
</template>

<style scoped>
.item {
  display: flex;
  align-items: center;
  gap: var(--layout-gap);
  margin-bottom: var(--layout-gap);
}

.item > .item-main {
  min-width: 1px;
  flex-grow: 2;
}

.item.disabled > .item-main {
  opacity: 0.5;
  cursor: help;
}

.item .item-title-extra {
  opacity: 0.75;
  font-size: 0.8em;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-extra {
  opacity: 0.4;
  padding-right: 0.25rem;
}
</style>
