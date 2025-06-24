<script setup lang="ts">
import { type AnyResourceRead, type UserRead } from '@/api';
import { $t } from '@/i18n';
import { ProposedIcon, PublicOffIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { NFlex, NIcon, NSwitch, NTag } from 'naive-ui';
import { computed } from 'vue';

const props = defineProps<{
  resource: AnyResourceRead;
  disabled?: boolean;
  user?: UserRead | null;
}>();

const active = defineModel<boolean>('active');
const state = useStateStore();

const resTitle = computed(() => pickTranslation(props.resource.title, state.locale));

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
    <div class="item-main">
      <n-flex justify="space-between" align="center" :wrap="false">
        <n-flex align="center" :wrap="false">
          <n-switch v-model:value="active" :round="false" />
          <span class="text-medium">{{ resTitle || '???' }}</span>
          <n-icon
            v-if="user && resource.proposed"
            size="medium"
            :component="ProposedIcon"
            :title="$t('resources.proposed')"
            color="var(--warning-color)"
          />
          <n-icon
            v-else-if="user && !resource.public"
            size="medium"
            :component="PublicOffIcon"
            :title="$t('resources.notPublic')"
            color="var(--error-color)"
          />
        </n-flex>
        <n-tag
          size="small"
          :title="`${$t('common.level')}: ${state.textLevelLabels[props.resource.level]}`"
        >
          {{ state.textLevelLabels[props.resource.level] }}
        </n-tag>
      </n-flex>
    </div>
  </n-flex>
</template>

<style scoped>
.item > .item-main {
  min-width: 1px;
  flex: 2;
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
