<script setup lang="ts">
import { prioritizedMetadataKeys, type AnyResourceRead, type UserRead } from '@/api';
import { $t } from '@/i18n';
import { ProposedIcon, PublicIcon, PublicOffIcon } from '@/icons';
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

const desc = computed<string>(() => {
  const m: string[] = [];
  const data = props.resource.meta || [];

  // prioritized metadata goes first
  prioritizedMetadataKeys.forEach((p: string) => {
    const v = data.find((d) => d.key === p)?.value;
    if (v) m.push(v);
  });
  // resource type
  if (props.resource.resourceType)
    m.push($t(`resources.types.${props.resource.resourceType}.label`));
  // join metadata to string
  return m.join(', ');
});
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
      <n-flex justify="space-between" align="center" :wrap="false">
        {{ resTitle || '???' }}
        <n-tag
          size="small"
          :title="`${$t('common.level')}: ${state.textLevelLabels[props.resource.level]}`"
        >
          {{ state.textLevelLabels[props.resource.level] }}
        </n-tag>
      </n-flex>
      <div class="text-mini translucent ellipsis">
        {{ desc }}
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
