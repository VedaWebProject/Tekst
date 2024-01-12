<script setup lang="ts">
import type { AnyResourceRead, UserRead } from '@/api';
import { NSpace, NDropdown, NEllipsis, NIcon, NListItem, NThing, NButton } from 'naive-ui';
import { computed, type Component, h } from 'vue';
import ResourceInfoWidget from '@/components/browse/widgets/ResourceInfoWidget.vue';
import ResourcePublicationStatus from '@/components/ResourcePublicationStatus.vue';
import TranslationDisplay from './TranslationDisplay.vue';
import { useStateStore } from '@/stores';
import { $t } from '@/i18n';
import ResourceIsVersionInfo from '@/components/ResourceIsVersionInfo.vue';

import MoreVertOutlined from '@vicons/material/MoreVertOutlined';
import DeleteFilled from '@vicons/material/DeleteFilled';
import SettingsFilled from '@vicons/material/SettingsFilled';
import FlagFilled from '@vicons/material/FlagFilled';
import FlagOutlined from '@vicons/material/FlagOutlined';
import PublicFilled from '@vicons/material/PublicFilled';
import PublicOffFilled from '@vicons/material/PublicOffFilled';
import PersonFilled from '@vicons/material/PersonFilled';
import EditNoteOutlined from '@vicons/material/EditNoteOutlined';
import AltRouteOutlined from '@vicons/material/AltRouteOutlined';
import UserDisplay from './UserDisplay.vue';

const props = defineProps<{
  targetResource: AnyResourceRead;
  currentUser?: UserRead;
}>();

const emit = defineEmits([
  'transferClick',
  'proposeClick',
  'unproposeClick',
  'publishClick',
  'unpublishClick',
  'settingsClick',
  'unitsClick',
  'createVersionClick',
  'deleteClick',
]);

const state = useStateStore();

const isOwnerOrAdmin = computed(
  () =>
    props.currentUser &&
    (props.currentUser.isSuperuser || props.currentUser.id === props.targetResource.ownerId)
);

const canDelete = computed(
  () => isOwnerOrAdmin.value && !props.targetResource.public && !props.targetResource.proposed
);

const canPropose = computed(() => isOwnerOrAdmin.value && !props.targetResource.public);

const actionOptions = computed(() => [
  ...(canPropose.value
    ? [
        {
          label: $t('resources.proposeAction'),
          key: 'propose',
          icon: renderIcon(FlagFilled),
          disabled:
            !canPropose.value ||
            props.targetResource.public ||
            props.targetResource.proposed ||
            !!props.targetResource.originalId,
          action: () => emit('proposeClick', props.targetResource),
        },
        {
          label: $t('resources.unproposeAction'),
          key: 'unpropose',
          icon: renderIcon(FlagOutlined),
          disabled:
            !canPropose.value ||
            !props.targetResource.proposed ||
            props.targetResource.public ||
            !!props.targetResource.originalId,
          action: () => emit('unproposeClick', props.targetResource),
        },
        {
          type: 'divider',
          key: 'proposalDivider',
        },
      ]
    : []),
  ...(props.currentUser?.isSuperuser
    ? [
        {
          label: $t('resources.publishAction'),
          key: 'publish',
          icon: renderIcon(PublicFilled),
          disabled:
            !props.currentUser?.isSuperuser ||
            !props.targetResource.proposed ||
            props.targetResource.public ||
            !!props.targetResource.originalId,
          action: () => emit('publishClick', props.targetResource),
        },
        {
          label: $t('resources.unpublishAction'),
          key: 'unpublish',
          icon: renderIcon(PublicOffFilled),
          disabled:
            !props.currentUser?.isSuperuser ||
            !props.targetResource.public ||
            !!props.targetResource.originalId,
          action: () => emit('unpublishClick', props.targetResource),
        },
        {
          type: 'divider',
          key: 'publicationDivider',
        },
      ]
    : []),
  {
    label: $t('resources.settingsAction'),
    key: 'settings',
    icon: renderIcon(SettingsFilled),
    disabled: !props.targetResource.writable,
    action: () => emit('settingsClick', props.targetResource),
  },
  {
    label: $t('resources.unitsAction'),
    key: 'units',
    icon: renderIcon(EditNoteOutlined),
    disabled: !props.targetResource.writable,
    action: () => emit('unitsClick', props.targetResource),
  },
  {
    label: $t('resources.createVersionAction'),
    key: 'version',
    icon: renderIcon(AltRouteOutlined),
    disabled: !!props.targetResource.originalId,
    action: () => emit('createVersionClick', props.targetResource),
  },
  {
    type: 'divider',
    key: 'editDivider',
  },
  {
    label: $t('resources.transferAction'),
    key: 'transfer',
    icon: renderIcon(PersonFilled),
    disabled: !isOwnerOrAdmin.value || props.targetResource.public || props.targetResource.proposed,
    action: () => emit('transferClick', props.targetResource),
  },
  {
    label: $t('general.deleteAction'),
    key: 'delete',
    icon: renderIcon(DeleteFilled),
    disabled: !canDelete.value,
    action: () => emit('deleteClick', props.targetResource),
  },
]);

const showActionsDropdown = computed(
  () => !!actionOptions.value.filter((o) => !!o.label && !o.disabled).length
);

function renderIcon(icon: Component) {
  return () => h(NIcon, null, { default: () => h(icon) });
}

function handleActionSelect(key: string) {
  actionOptions.value.find((o) => o.key === key)?.action?.();
}
</script>

<template>
  <n-list-item class="resource-list-item">
    <n-thing :title="targetResource.title" content-style="margin-top: 8px">
      <template #header-extra>
        <n-space>
          <n-dropdown
            v-if="showActionsDropdown"
            :options="actionOptions"
            :size="state.dropdownSize"
            to="#app-container"
            trigger="click"
            @select="handleActionSelect"
          >
            <n-button quaternary circle :focusable="false">
              <template #icon>
                <n-icon :component="MoreVertOutlined" />
              </template>
            </n-button>
          </n-dropdown>
          <ResourceInfoWidget :resource="targetResource" />
        </n-space>
      </template>

      <template #description>
        <UserDisplay v-if="targetResource.owner" :user="targetResource.owner" size="tiny" />
        <ResourcePublicationStatus :resource="targetResource" size="tiny" />
        <ResourceIsVersionInfo :resource="targetResource" size="tiny" />
      </template>

      <template v-if="targetResource.description?.length">
        <n-ellipsis :tooltip="false" :line-clamp="2" expand-trigger="click">
          <TranslationDisplay :value="targetResource.description" />
        </n-ellipsis>
      </template>
    </n-thing>
  </n-list-item>
</template>

<style>
.resource-list-item:first-child {
  padding-top: 0;
}
.resource-list-item:last-child {
  padding-bottom: 0;
}
.resource-list-item .n-thing-header__title {
  color: var(--accent-color) !important;
}
</style>
