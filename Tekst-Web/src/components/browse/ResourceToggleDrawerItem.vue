<script setup lang="ts">
import { computed } from 'vue';
import { NFlex, NSwitch, NIcon } from 'naive-ui';
import { $t } from '@/i18n';
import MetadataDisplayMinimal from '@/components/resource/MetadataDisplayMinimal.vue';
import type { AnyResourceRead, UserRead } from '@/api';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import { PublicIcon, ProposedIcon, PublicOffIcon } from '@/icons';

const props = defineProps<{
  resource: AnyResourceRead;
  disabled?: boolean;
  user?: UserRead;
}>();

const active = defineModel<boolean>('active');

const infoTooltip = computed(() =>
  props.disabled ? $t('browse.locationResourceNoData') : undefined
);
</script>

<template>
  <n-flex
    align="center"
    :wrap="false"
    class="item mb-sm"
    :class="disabled && 'disabled'"
    :title="infoTooltip"
  >
    <n-switch v-model:value="active" :round="false" />
    <div class="item-main">
      <div>
        <translation-display v-if="resource.title" :value="resource.title" />
      </div>
      <div class="text-mini translucent ellipsis">
        <metadata-display-minimal :resource="resource" />
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
  </n-flex>
</template>

<style scoped>
.item > .item-main {
  min-width: 1px;
  flex-grow: 2;
}

.item.disabled > .item-main {
  opacity: 0.5;
  cursor: help;
}

.item-extra {
  opacity: 0.4;
  padding-right: 0.25rem;
}
</style>
