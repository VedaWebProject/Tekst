<script setup lang="ts">
import type { AnyResourceRead, UserRead } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import ContentEditWidget from '@/components/resource/ContentEditWidget.vue';
import ResourceInfoTags from '@/components/resource/ResourceInfoTags.vue';
import ResourceInfoWidget from '@/components/resource/ResourceInfoWidget.vue';
import ResourceSettingsWidget from '@/components/resource/ResourceSettingsWidget.vue';
import UserDisplay from '@/components/user/UserDisplay.vue';
import { $t } from '@/i18n';
import { useResourcesStore, useStateStore } from '@/stores';
import {
  NBadge,
  NButton,
  NCollapseItem,
  NDropdown,
  NFlex,
  NIcon,
  type DropdownOption,
} from 'naive-ui';
import { computed } from 'vue';

import {
  CorrectionNoteIcon,
  DeleteIcon,
  DownloadIcon,
  MoreIcon,
  ProposedIcon,
  PublicIcon,
  PublicOffIcon,
  ReviewIcon,
  UnproposedIcon,
  UploadIcon,
  UserIcon,
  VersionIcon,
} from '@/icons';
import { pickTranslation, renderIcon } from '@/utils';
import { useRouter } from 'vue-router';

const props = defineProps<{
  resource: AnyResourceRead;
  user?: UserRead | null;
}>();

const emit = defineEmits([
  'transferClick',
  'proposeClick',
  'unproposeClick',
  'publishClick',
  'unpublishClick',
  'reqVersionIntegrationClick',
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

const isOwner = computed(() => (props.user?.id ?? 'noid') === props.resource.ownerId);
const isOwnerOrAdmin = computed(() => isOwner.value || !!props.user?.isSuperuser);

const resourceTitle = computed(() => pickTranslation(props.resource.title, state.locale));

const actionOptions = computed<DropdownOption[] | null>(() =>
  !!props.user
    ? [
        ...(props.resource.writable
          ? [
              {
                type: 'group',
                label: $t('common.content', 2),
                children: [
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
                        },
                      ]
                    : []),
                  {
                    label: $t('resources.transferAction'),
                    key: 'transfer',
                    icon: renderIcon(UserIcon),
                    action: () => emit('transferClick', props.resource),
                  },
                  ...(!!props.resource.originalId && props.resource.ownerId === props.user?.id
                    ? [
                        {
                          label: $t('resources.reqVersionIntegrationAction'),
                          key: 'reqVersionIntegration',
                          icon: renderIcon(ReviewIcon),
                          disabled:
                            resources.all.find((r) => r.id === props.resource.originalId)
                              ?.ownerId === props.resource.ownerId,
                          action: () => emit('reqVersionIntegrationClick', props.resource),
                        },
                      ]
                    : []),
                ],
              },
            ]
          : []),
        {
          type: 'group',
          label: $t('common.general'),
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
                    label: $t('common.delete'),
                    key: 'delete',
                    icon: renderIcon(DeleteIcon),
                    disabled: props.resource.public || props.resource.proposed,
                    action: () => emit('deleteClick', props.resource),
                  },
                ]
              : []),
          ],
        },
      ]
    : null
);

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
  <n-collapse-item class="res-item" :name="resource.id">
    <template #header>
      <n-flex align="center" style="width: 100%">
        <b>{{ resourceTitle }}</b>
        <resource-info-tags
          v-if="!state.smallScreen"
          :resource="resource"
          justify="flex-start"
          reverse
          style="flex: 2"
        />
      </n-flex>
    </template>

    <resource-info-tags
      v-if="state.smallScreen"
      :resource="resource"
      justify="flex-start"
      reverse
      class="mb-md"
    />

    <n-flex style="flex-wrap: wrap-reverse">
      <user-display :user="resource.owner || undefined" size="small" :system="resource.public" />
      <n-flex justify="flex-end" :wrap="false" style="flex: 2">
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

        <resource-settings-widget v-if="resource.writable" :resource="resource" />
        <content-edit-widget v-if="resource.writable" :resource="resource" />
        <resource-info-widget :resource="resource" />

        <n-dropdown
          v-if="!!actionOptions?.length"
          :options="actionOptions"
          trigger="hover"
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
    </n-flex>

    <div v-if="resource.subtitle.length" class="mt-md">
      <translation-display :value="resource.subtitle" />
    </div>
  </n-collapse-item>
</template>

<style scoped>
.res-item:first-child {
  padding-top: 0;
}

.res-item:last-child {
  padding-bottom: 0;
}

.res-item :deep(.n-thing > .n-thing-main) {
  max-width: 100%;
}

.res-item :deep(.n-thing > .n-thing-main .n-thing-header) {
  align-items: flex-start;
  flex-wrap: wrap;
}
</style>
