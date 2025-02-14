<script setup lang="ts">
import type { AnyResourceRead, UserRead } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import ResourceExportWidget from '@/components/resource/ResourceExportWidget.vue';
import ResourceInfoWidget from '@/components/resource/ResourceInfoWidget.vue';
import ResourceIsVersionInfo from '@/components/resource/ResourceIsVersionInfo.vue';
import ResourcePublicationStatus from '@/components/resource/ResourcePublicationStatus.vue';
import UserDisplay from '@/components/user/UserDisplay.vue';
import { $t } from '@/i18n';
import { useResourcesStore, useStateStore } from '@/stores';
import {
  NBadge,
  NButton,
  NDropdown,
  NEllipsis,
  NFlex,
  NIcon,
  NListItem,
  NThing,
  type DropdownOption,
} from 'naive-ui';
import { computed } from 'vue';

import {
  CorrectionNoteIcon,
  DeleteIcon,
  DownloadIcon,
  EditIcon,
  MoreIcon,
  ProposedIcon,
  PublicIcon,
  PublicOffIcon,
  SettingsIcon,
  UnproposedIcon,
  UploadIcon,
  UserIcon,
  VersionIcon,
} from '@/icons';
import { pickTranslation, renderIcon } from '@/utils';
import { useRouter } from 'vue-router';

const props = defineProps<{
  resource: AnyResourceRead;
  currentUser?: UserRead | null;
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
]);

const state = useStateStore();
const router = useRouter();
const resources = useResourcesStore();

const isOwner = computed(() => (props.currentUser?.id ?? 'noid') === props.resource.ownerId);
const isOwnerOrAdmin = computed(() => isOwner.value || !!props.currentUser?.isSuperuser);

const resourceTitle = computed(() => pickTranslation(props.resource.title, state.locale));

const actionOptions = computed(() => [
  ...(props.resource.writable
    ? [
        {
          type: 'group',
          label: $t('general.editAction'),
          children: [
            {
              label: $t('general.settings'),
              key: 'settings',
              icon: renderIcon(SettingsIcon),
              action: () => emit('settingsClick', props.resource),
            },
            {
              label: $t('resources.contentsAction'),
              key: 'contents',
              icon: renderIcon(EditIcon),
              action: () => emit('contentsClick', props.resource),
            },
            {
              label: $t('resources.downloadTemplateAction'),
              key: 'template',
              icon: renderIcon(DownloadIcon),
              action: () => emit('downloadTemplateClick', props.resource),
            },
            {
              label: $t('resources.importAction'),
              key: 'import',
              icon: renderIcon(UploadIcon),
              action: () => emit('importClick', props.resource),
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
            ...(!props.resource.proposed && !props.resource.public
              ? [
                  {
                    label: $t('resources.proposeAction'),
                    key: 'propose',
                    disabled: !!props.resource.originalId,
                    icon: renderIcon(ProposedIcon),
                    action: () => emit('proposeClick', props.resource),
                  },
                ]
              : []),
            ...(props.resource.proposed && !props.resource.public
              ? [
                  {
                    label: $t('resources.unproposeAction'),
                    key: 'unpropose',
                    disabled: !!props.resource.originalId,
                    icon: renderIcon(UnproposedIcon),
                    action: () => emit('unproposeClick', props.resource),
                  },
                ]
              : []),
            ...(props.currentUser?.isSuperuser && !props.resource.public && props.resource.proposed
              ? [
                  {
                    label: $t('resources.publishAction'),
                    key: 'publish',
                    disabled: !!props.resource.originalId,
                    icon: renderIcon(PublicIcon),
                    action: () => emit('publishClick', props.resource),
                  },
                ]
              : []),
            ...(props.currentUser?.isSuperuser && props.resource.public && !props.resource.proposed
              ? [
                  {
                    label: $t('resources.unpublishAction'),
                    key: 'unpublish',
                    disabled: !!props.resource.originalId,
                    icon: renderIcon(PublicOffIcon),
                    action: () => emit('unpublishClick', props.resource),
                  },
                ]
              : []),
            {
              label: $t('resources.transferAction'),
              key: 'transfer',
              icon: renderIcon(UserIcon),
              disabled: props.resource.public || props.resource.proposed,
              action: () => emit('transferClick', props.resource),
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
        disabled: !!props.resource.originalId,
        action: () => emit('createVersionClick', props.resource),
      },
      ...(isOwnerOrAdmin.value
        ? [
            {
              label: $t('general.deleteAction'),
              key: 'delete',
              icon: renderIcon(DeleteIcon),
              disabled: props.resource.public || props.resource.proposed,
              action: () => emit('deleteClick', props.resource),
            },
          ]
        : []),
    ],
  },
]);

function handleActionSelect(o: DropdownOption & { action?: () => void }) {
  o.action?.();
}

function handleCorrectionsClick() {
  router.push({
    name: 'resourceCorrections',
    params: { textSlug: state.text?.slug, resId: props.resource.id },
  });
}
</script>

<template>
  <n-list-item class="resource-list-item">
    <n-thing content-style="margin-top: 8px">
      <template #header>
        <span class="b">
          {{ resourceTitle }}
        </span>
      </template>
      <template #header-extra>
        <n-flex>
          <n-badge
            v-if="!!resources.correctionsCount[resource.id]"
            :value="resources.correctionsCount[resource.id]"
            :max="100"
          >
            <content-container-header-widget
              :title="$t('resources.correctionNotesAction')"
              :icon-component="CorrectionNoteIcon"
              @click="handleCorrectionsClick()"
            />
          </n-badge>
          <resource-export-widget :resource="resource" />
          <resource-info-widget :resource="resource" />
          <n-dropdown
            :options="actionOptions"
            trigger="click"
            placement="bottom-end"
            @select="(_, o) => handleActionSelect(o)"
          >
            <n-button quaternary circle :focusable="false">
              <template #icon>
                <n-icon :component="MoreIcon" />
              </template>
            </n-button>
          </n-dropdown>
        </n-flex>
      </template>

      <template #description>
        <user-display v-if="resource.owner" :user="resource.owner" size="tiny" class="mb-lg" />
        <n-flex vertical>
          <resource-publication-status :resource="resource" size="tiny" />
          <resource-is-version-info v-if="resource.originalId" :resource="resource" size="tiny" />
        </n-flex>
      </template>

      <template v-if="resource.description.length">
        <n-ellipsis :tooltip="false" :line-clamp="2" expand-trigger="click">
          <translation-display :value="resource.description" />
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
