<script setup lang="ts">
import type { AnyResourceRead, UserRead } from '@/api';
import CopyToClipboardButton from '@/components/generic/CopyToClipboardButton.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import ResourceExportModal from '@/components/resource/ResourceExportModal.vue';
import ResourceInfoContent from '@/components/resource/ResourceInfoContent.vue';
import ResourceInfoTags from '@/components/resource/ResourceInfoTags.vue';
import env from '@/env';
import { $t } from '@/i18n';
import {
  BookIcon,
  CorrectionNoteIcon,
  DeleteIcon,
  DownloadIcon,
  EditIcon,
  MoreIcon,
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
import { useResourcesStore, useStateStore } from '@/stores';
import { pickTranslation, renderIcon } from '@/utils';
import { NBadge, NButton, NCollapseItem, NFlex, NIcon, type DropdownOption } from 'naive-ui';
import type { Type } from 'naive-ui/es/button/src/interface';
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps<{
  resource: AnyResourceRead;
  user?: UserRead | null;
  shown?: boolean;
}>();

const emit = defineEmits([
  'browseClick',
  'setOwnersClick',
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

const isOwner = computed(() => !!props.resource.ownerIds?.includes(props.user?.id ?? 'noid'));
const isOwnerOrAdmin = computed(() => isOwner.value || !!props.user?.isSuperuser);

const resTitle = computed(() => pickTranslation(props.resource.title, state.locale));
const resInfoUrl = computed(
  () =>
    `${origin}${env.WEB_PATH_STRIPPED}/texts/${state.text?.slug || '???'}/resources#id=${props.resource.id}`
);

const actionOptions = computed<DropdownOption[]>(() => [
  {
    type: 'group',
    label: $t('common.general'),
    children: [
      {
        label:
          pickTranslation(state.pf?.state.navTranslations.browse, state.locale) ||
          $t('common.browse'),
        key: 'browse',
        icon: renderIcon(BookIcon),
        action: () => emit('browseClick', props.resource),
      },
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
            {
              label:
                $t('resources.correctionNotesAction') +
                ` (${resources.correctionsCount[props.resource.id]})`,
              key: 'corrections',
              icon: renderIcon(CorrectionNoteIcon),
              action: handleCorrectionsClick,
              disabled: resources.correctionsCount[props.resource.id] <= 0,
              statusType: resources.correctionsCount[props.resource.id] > 0 ? 'warning' : undefined,
            },
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
            ...(!props.resource.proposed && !props.resource.public && !props.resource.originalId
              ? [
                  {
                    label: $t('resources.proposeAction'),
                    key: 'propose',
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
                    disabled: !!props.resource.originalId,
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
            ...(!!props.resource.originalId &&
            props.user &&
            props.resource.ownerIds.includes(props.user.id)
              ? [
                  {
                    label: $t('resources.reqVersionIntegration.action'),
                    key: 'reqVersionIntegration',
                    icon: renderIcon(ReviewIcon),
                    disabled:
                      resources.all
                        .find((r) => r.id === props.resource.originalId)
                        ?.ownerIds.includes(props.user.id) ||
                      !resources.all.find((r) => r.id === props.resource.originalId)?.ownerIds
                        .length,
                    action: () => emit('reqVersionIntegrationClick', props.resource),
                    statusType: 'success',
                  },
                ]
              : []),
            ...(props.user?.isSuperuser || (!props.resource.public && !props.resource.proposed)
              ? [
                  {
                    label: $t('resources.setOwnersAction'),
                    key: 'setOwners',
                    icon: renderIcon(UserIcon),
                    action: () => emit('setOwnersClick', props.resource),
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
        <b>{{ resTitle }}</b>
        <n-badge
          :show="resources.correctionsCount[props.resource.id] > 0"
          :title="$t('resources.hasCorrectionsTip')"
        >
          <template #value>
            <n-flex :wrap="false" size="small">
              <n-icon :component="CorrectionNoteIcon" />
            </n-flex>
          </template>
        </n-badge>
        <resource-info-tags
          v-if="state.vw >= 900 && !shown"
          :resource="resource"
          justify="flex-end"
          style="flex: 2"
        />
      </n-flex>
    </template>

    <n-flex justify="space-between" align="center" class="mb-lg" style="flex-wrap: wrap-reverse">
      <n-flex size="small">
        <n-button secondary size="tiny" @click="emit('browseClick', props.resource)">
          <template #icon>
            <n-icon :component="BookIcon" />
          </template>
          {{
            pickTranslation(state.pf?.state.navTranslations.browse, state.locale) ||
            $t('common.browse')
          }}
        </n-button>
        <copy-to-clipboard-button
          v-if="state.text"
          tertiary
          size="tiny"
          :text="resInfoUrl"
          :title="$t('resources.copyInfoUrlTip')"
          show-msg
        >
          {{ $t('resources.copyInfoUrl') }}
        </copy-to-clipboard-button>
      </n-flex>
      <resource-info-tags :resource="resource" />
    </n-flex>

    <div>
      <resource-info-content :resource="resource" />
      <div class="gray-box mb-lg">
        <icon-heading level="3" :icon="MoreIcon">
          {{ $t('common.actions') }}
        </icon-heading>
        <div class="res-item-actions">
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
      </div>
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
