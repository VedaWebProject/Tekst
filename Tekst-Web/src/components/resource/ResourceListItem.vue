<script setup lang="ts">
import type { AnyResourceRead, UserRead } from '@/api';
import {
  NSpace,
  NDropdown,
  NEllipsis,
  NIcon,
  NListItem,
  NThing,
  NButton,
  type DropdownOption,
} from 'naive-ui';
import { computed, type Component, h } from 'vue';
import ResourceInfoWidget from '@/components/resource/ResourceInfoWidget.vue';
import ResourcePublicationStatus from '@/components/resource/ResourcePublicationStatus.vue';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import { useStateStore } from '@/stores';
import { $t } from '@/i18n';
import ResourceIsVersionInfo from '@/components/resource/ResourceIsVersionInfo.vue';
import UserDisplay from '@/components/user/UserDisplay.vue';

import {
  MoreIcon,
  DeleteIcon,
  SettingsIcon,
  ProposedIcon,
  UnproposedIcon,
  PublicIcon,
  PublicOffIcon,
  UserIcon,
  EditNoteIcon,
  VersionIcon,
  DownloadIcon,
  UploadIcon,
} from '@/icons';

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
  'contentsClick',
  'createVersionClick',
  'deleteClick',
  'downloadTemplateClick',
  'importClick',
  'exportClick',
]);

const state = useStateStore();

const isOwnerOrAdmin = computed(
  () =>
    props.currentUser &&
    (props.currentUser.isSuperuser || props.currentUser.id === props.targetResource.ownerId)
);

const actionOptions = computed(() => [
  ...(props.targetResource.writable
    ? [
        {
          type: 'group',
          label: $t('general.editAction'),
          children: [
            {
              label: $t('resources.settingsAction'),
              key: 'settings',
              icon: renderIcon(SettingsIcon),
              action: () => emit('settingsClick', props.targetResource),
            },
            {
              label: $t('resources.contentsAction'),
              key: 'contents',
              icon: renderIcon(EditNoteIcon),
              action: () => emit('contentsClick', props.targetResource),
            },
            {
              label: $t('resources.downloadTemplateAction'),
              key: 'template',
              icon: renderIcon(DownloadIcon),
              action: () => emit('downloadTemplateClick', props.targetResource),
            },
            {
              label: $t('resources.importAction'),
              key: 'import',
              icon: renderIcon(UploadIcon),
              action: () => emit('importClick', props.targetResource),
            },
          ],
        },
      ]
    : []),
  ...(isOwnerOrAdmin.value
    ? [
        {
          type: 'group',
          label: $t('general.status'),
          children: [
            ...(!props.targetResource.proposed && !props.targetResource.public
              ? [
                  {
                    label: $t('resources.proposeAction'),
                    key: 'propose',
                    disabled: !!props.targetResource.originalId,
                    icon: renderIcon(ProposedIcon),
                    action: () => emit('proposeClick', props.targetResource),
                  },
                ]
              : []),
            ...(props.targetResource.proposed && !props.targetResource.public
              ? [
                  {
                    label: $t('resources.unproposeAction'),
                    key: 'unpropose',
                    disabled: !!props.targetResource.originalId,
                    icon: renderIcon(UnproposedIcon),
                    action: () => emit('unproposeClick', props.targetResource),
                  },
                ]
              : []),
            ...(props.currentUser?.isSuperuser &&
            !props.targetResource.public &&
            props.targetResource.proposed
              ? [
                  {
                    label: $t('resources.publishAction'),
                    key: 'publish',
                    disabled: !!props.targetResource.originalId,
                    icon: renderIcon(PublicIcon),
                    action: () => emit('publishClick', props.targetResource),
                  },
                ]
              : []),
            ...(props.currentUser?.isSuperuser &&
            props.targetResource.public &&
            !props.targetResource.proposed
              ? [
                  {
                    label: $t('resources.unpublishAction'),
                    key: 'unpublish',
                    disabled: !!props.targetResource.originalId,
                    icon: renderIcon(PublicOffIcon),
                    action: () => emit('unpublishClick', props.targetResource),
                  },
                ]
              : []),
            {
              label: $t('resources.transferAction'),
              key: 'transfer',
              icon: renderIcon(UserIcon),
              disabled: props.targetResource.public || props.targetResource.proposed,
              action: () => emit('transferClick', props.targetResource),
            },
          ],
        },
      ]
    : []),
  {
    type: 'group',
    label: $t('general.general'),
    children: [
      {
        label: $t('resources.createVersionAction'),
        key: 'version',
        icon: renderIcon(VersionIcon),
        disabled: !!props.targetResource.originalId,
        action: () => emit('createVersionClick', props.targetResource),
      },
      ...(isOwnerOrAdmin.value
        ? [
            {
              label: $t('general.deleteAction'),
              key: 'delete',
              icon: renderIcon(DeleteIcon),
              disabled: props.targetResource.public || props.targetResource.proposed,
              action: () => emit('deleteClick', props.targetResource),
            },
          ]
        : []),
    ],
  },
]);

function renderIcon(icon: Component) {
  return () => h(NIcon, null, { default: () => h(icon) });
}

function handleActionSelect(o: DropdownOption & { action?: () => void }) {
  o.action?.();
}
</script>

<template>
  <n-list-item class="resource-list-item">
    <n-thing :title="targetResource.title" content-style="margin-top: 8px">
      <template #header-extra>
        <n-space>
          <n-dropdown
            :options="actionOptions"
            :size="state.dropdownSize"
            to="#app-container"
            trigger="click"
            @select="(_, o) => handleActionSelect(o)"
          >
            <n-button quaternary circle :focusable="false">
              <template #icon>
                <n-icon :component="MoreIcon" />
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
