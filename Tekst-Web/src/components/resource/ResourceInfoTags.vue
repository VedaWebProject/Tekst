<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import { $t } from '@/i18n';
import {
  CommunityIcon,
  LevelsIcon,
  ProposedIcon,
  PublicIcon,
  PublicOffIcon,
  ResourceIcon,
  VersionIcon,
} from '@/icons';
import { useAuthStore, useResourcesStore, useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { NFlex, NIcon, NTag } from 'naive-ui';
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    resource: AnyResourceRead;
    size?: 'small' | 'medium' | 'large';
  }>(),
  {
    size: 'small',
  }
);

const state = useStateStore();
const auth = useAuthStore();
const resources = useResourcesStore();

const originalTitle = pickTranslation(
  resources.ofText.find((r) => r.id == props.resource.originalId)?.title,
  state.locale
);

const publicationStatusType = computed(() =>
  props.resource.public ? 'success' : props.resource.proposed ? 'warning' : 'error'
);
const publicationStatusIcon = computed(() =>
  props.resource.public ? PublicIcon : props.resource.proposed ? ProposedIcon : PublicOffIcon
);
const publicationStatusText = computed(() =>
  props.resource.public
    ? $t('resources.public')
    : props.resource.proposed
      ? $t('resources.proposed')
      : $t('resources.notPublic')
);

const accessSharesTip = computed(() => {
  const sharedWriteNames = props.resource.sharedWriteUsers
    ?.map((u) => u.name || `@${u.username}`)
    .join(', ');
  const sharedReadNames = props.resource.sharedReadUsers
    ?.map((u) => u.name || `@${u.username}`)
    .join(', ');
  return (
    `${$t('models.resource.sharedWrite')}: ${sharedWriteNames || '–'}; ` +
    `${$t('models.resource.sharedRead')}: ${sharedReadNames || '–'}`
  );
});
</script>

<template>
  <n-flex v-bind="$attrs" :size="size">
    <n-tag v-if="!resource.originalId && !!auth.user" :type="publicationStatusType" :size="size">
      <template #icon>
        <n-icon :component="publicationStatusIcon" />
      </template>
      {{ publicationStatusText }}
    </n-tag>
    <n-tag v-if="!!resource.originalId" type="info" :size="size">
      <template #icon>
        <n-icon :component="VersionIcon" />
      </template>
      {{ $t('resources.versionOf', { title: originalTitle || $t('resources.unknownOriginal') }) }}
    </n-tag>
    <n-tag
      v-if="!!(resource.sharedRead.length + resource.sharedWrite.length)"
      :size="size"
      :title="accessSharesTip"
    >
      <template #icon>
        <n-icon :component="CommunityIcon" />
      </template>
      {{
        $t('resources.shared', { count: resource.sharedRead.length + resource.sharedWrite.length })
      }}
    </n-tag>
    <n-tag :size="size" :title="$t('common.level')">
      <template #icon>
        <n-icon :component="LevelsIcon" />
      </template>
      {{ state.textLevelLabels[resource.level] }}
    </n-tag>
    <n-tag :size="size" :title="$t('models.resource.resourceType')">
      <template #icon>
        <n-icon :component="ResourceIcon" />
      </template>
      {{ $t(`resources.types.${resource.resourceType}.label`) }}
    </n-tag>
  </n-flex>
</template>
