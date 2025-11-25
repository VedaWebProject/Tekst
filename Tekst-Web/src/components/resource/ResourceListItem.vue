<script setup lang="ts">
import type { AnyResourceRead, UserRead } from '@/api';
import ResourceInfoTags from '@/components/resource/ResourceInfoTags.vue';
import { $t } from '@/i18n';
import { useResourcesStore, useStateStore } from '@/stores';
import { NButton, NCollapseItem, NFlex, type DropdownOption } from 'naive-ui';
import { computed, ref } from 'vue';

import ResourceExportModal from '@/components/resource/ResourceExportModal.vue';
import ResourceInfoContent from '@/components/resource/ResourceInfoContent.vue';
import {
  CorrectionNoteIcon,
  DeleteIcon,
  DownloadIcon,
  EditIcon,
  ProposedIcon,
  PublicIcon,
  PublicOffIcon,
  ReviewIcon,
  SettingsIcon,
  UnproposedIcon,
  UploadIcon,
  UserIcon,
  VersionIcon,
} from '@/icons';
import { pickTranslation, renderIcon } from '@/utils';
import type { Type } from 'naive-ui/es/button/src/interface';
import { useRouter } from 'vue-router';

const props = defineProps<{
  resource: AnyResourceRead;
  user?: UserRead | null;
  shown?: boolean;
}>();

const emit = defineEmits([
  'transferClick',
  'proposeClick',
  'unproposeClick',
  'publishClick',
  'unpublishClick',
  'reqVersionIntegrationClick',
  'settingsClick',
  'editContentsClick',
  'createVersionClick',
  'deleteClick',
  'downloadTemplateClick',
  'importClick',
]);

const state = useStateStore();
const router = useRouter();
const resources = useResourcesStore();

const showExport = ref(false);

const isOwner = computed(() => (props.user?.id ?? 'noid') === props.resource.ownerId);
const isOwnerOrAdmin = computed(() => isOwner.value || !!props.user?.isSuperuser);

const resourceTitle = computed(() => pickTranslation(props.resource.title, state.locale));

const actionOptions = computed<DropdownOption[]>(() => [
  {
    type: 'group',
    label: $t('common.general'),
    children: [
      ...(!props.resource.originalId && props.user
        ? [
            {
              label: $t('resources.createVersionAction'),
              key: 'version',
              icon: renderIcon(VersionIcon),
              action: () => emit('createVersionClick', props.resource),
            },
          ]
        : []),
      ...(isOwnerOrAdmin.value
        ? [
            {
              label: $t('common.settings'),
              key: 'settings',
              icon: renderIcon(SettingsIcon),
              action: () => emit('settingsClick', props.resource),
            },
            {
              label: $t('resources.transferAction'),
              key: 'transfer',
              icon: renderIcon(UserIcon),
              action: () => emit('transferClick', props.resource),
            },
            {
              label: $t('common.delete'),
              key: 'delete',
              icon: renderIcon(DeleteIcon),
              disabled: props.resource.public || props.resource.proposed,
              action: () => emit('deleteClick', props.resource),
              statusType: 'error',
            },
          ]
        : []),
    ],
  },
  {
    type: 'group',
    label: $t('common.content', 2),
    children: [
      {
        label: $t('common.export'),
        key: 'export',
        icon: renderIcon(DownloadIcon),
        action: () => {
          showExport.value = true;
        },
      },
      ...(props.resource.writable
        ? [
            ...(!!resources.correctionsCount[props.resource.id]
              ? [
                  {
                    label:
                      $t('resources.correctionNotesAction') +
                      ` (${resources.correctionsCount[props.resource.id]})`,
                    key: 'corrections',
                    icon: renderIcon(CorrectionNoteIcon),
                    action: handleCorrectionsClick,
                  },
                ]
              : []),
            {
              label: $t('browse.contents.widgets.contentEdit.title'),
              key: 'edit',
              icon: renderIcon(EditIcon),
              action: () => emit('editContentsClick', props.resource),
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
          ]
        : []),
    ],
  },
  ...(isOwnerOrAdmin.value
    ? [
        {
          type: 'group',
          label: $t('common.status'),
          children: [
            ...(!props.resource.proposed && !props.resource.public
              ? [
                  {
                    label: $t('resources.proposeAction'),
                    key: 'propose',
                    disabled: !!props.resource.originalId || !isOwner.value,
                    icon: renderIcon(ProposedIcon),
                    action: () => emit('proposeClick', props.resource),
                    statusType: 'warning',
                  },
                ]
              : []),
            ...(props.resource.proposed && !props.resource.public
              ? [
                  {
                    label: $t('resources.unproposeAction'),
                    key: 'unpropose',
                    disabled: !!props.resource.originalId || !isOwner.value,
                    icon: renderIcon(UnproposedIcon),
                    action: () => emit('unproposeClick', props.resource),
                    statusType: 'error',
                  },
                ]
              : []),
            ...(props.user?.isSuperuser && !props.resource.public && props.resource.proposed
              ? [
                  {
                    label: $t('resources.publishAction'),
                    key: 'publish',
                    disabled: !!props.resource.originalId,
                    icon: renderIcon(PublicIcon),
                    action: () => emit('publishClick', props.resource),
                    statusType: 'success',
                  },
                ]
              : []),
            ...(props.user?.isSuperuser && props.resource.public && !props.resource.proposed
              ? [
                  {
                    label: $t('resources.unpublishAction'),
                    key: 'unpublish',
                    disabled: !!props.resource.originalId,
                    icon: renderIcon(PublicOffIcon),
                    action: () => emit('unpublishClick', props.resource),
                    statusType: 'error',
                  },
                ]
              : []),
            ...(!!props.resource.originalId && props.resource.ownerId === props.user?.id
              ? [
                  {
                    label: $t('resources.reqVersionIntegrationAction'),
                    key: 'reqVersionIntegration',
                    icon: renderIcon(ReviewIcon),
                    disabled:
                      resources.all.find((r) => r.id === props.resource.originalId)?.ownerId ===
                      props.resource.ownerId,
                    action: () => emit('reqVersionIntegrationClick', props.resource),
                    statusType: 'success',
                  },
                ]
              : []),
          ],
        },
      ]
    : []),
]);

function handleCorrectionsClick() {
  router.push({
    name: 'resourceCorrections',
    params: { textSlug: state.text?.slug, resId: props.resource.id },
  });
}
</script>

<template>
  <n-collapse-item class="res-item" :name="resource.id">
    <template #header>
      <n-flex align="center" style="width: 100%">
        <b>{{ resourceTitle }}</b>
        <resource-info-tags
          v-if="!state.smallScreen && !shown"
          :resource="resource"
          justify="flex-start"
          reverse
          style="flex: 2"
        />
      </n-flex>
    </template>

    <div :style="{ 'padding-left': !state.smallScreen ? '20px' : undefined }">
      <div class="res-item-actions mb-lg">
        <template v-for="optGroup in actionOptions" :key="optGroup.key">
          <n-flex v-if="!!optGroup.children?.length" vertical>
            <div class="text-small translucent">{{ optGroup.label }}</div>
            <n-button
              v-for="opt in optGroup.children"
              :key="opt.key"
              secondary
              :type="opt.statusType as Type"
              :disabled="!!opt.disabled"
              @click="opt.action as () => void"
            >
              <template #icon>
                <component :is="opt.icon" />
              </template>
              {{ opt.label }}
            </n-button>
          </n-flex>
        </template>
      </div>

      <resource-info-content :resource="resource" />
    </div>

    <resource-export-modal v-model:show="showExport" :resource="resource" />
  </n-collapse-item>
</template>

<style scoped>
.res-item:first-child {
  padding-top: 0;
}

.res-item:last-child {
  padding-bottom: 0;
}

.res-item .res-item-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}
</style>
