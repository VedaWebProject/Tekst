<script setup lang="ts">
import { type AnyResourceRead, type UserRead } from '@/api';
import CopyToClipboardButton from '@/components/generic/CopyToClipboardButton.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import ResourceExportModal from '@/components/resource/ResourceExportModal.vue';
import ResourceInfoContent from '@/components/resource/ResourceInfoContent.vue';
import ResourceInfoTags from '@/components/resource/ResourceInfoTags.vue';
import UserDisplay from '@/components/user/UserDisplay.vue';
import { useUsers } from '@/composables/user';
import env from '@/env';
import { $t } from '@/i18n';
import {
  BookIcon,
  CorrectionNoteIcon,
  DeleteIcon,
  DownloadIcon,
  EditIcon,
  IntegratePatchIcon,
  MoreIcon,
  PatchIcon,
  ProposedIcon,
  PublicIcon,
  PublicOffIcon,
  SettingsIcon,
  StarIcon,
  StarOffIcon,
  UnproposedIcon,
  UploadIcon,
  UserIcon,
} from '@/icons';
import { useResourcesStore, useStateStore } from '@/stores';
import { pickTranslation, renderIcon } from '@/utils';
import {
  NAlert,
  NBadge,
  NButton,
  NCollapseItem,
  NFlex,
  NIcon,
  type ButtonType,
  type DropdownOption,
} from 'naive-ui';
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
  'supportClick',
  'unsupportClick',
  'publishClick',
  'unpublishClick',
  'reqPatchIntegrationClick',
  'settingsClick',
  'editContentsClick',
  'createPatchClick',
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

const {users} = useUsers(props.resource.supporters ?? undefined);

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
      ...(!props.resource.patchFor && props.user
        ? [
            {
              label: $t('resources.createPatchAction'),
              key: 'patch',
              icon: renderIcon(PatchIcon),
              action: () => emit('createPatchClick', props.resource),
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
  {
    type: 'group',
    label: $t('common.status'),
    children: [
      ...(isOwnerOrAdmin.value && !props.resource.proposed && !props.resource.public && !props.resource.patchFor
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
      ...(isOwnerOrAdmin.value && props.resource.proposed && !props.resource.public
        ? [
            {
              label: $t('resources.unproposeAction'),
              key: 'unpropose',
              disabled: !!props.resource.patchFor,
              icon: renderIcon(UnproposedIcon),
              action: () => emit('unproposeClick', props.resource),
              statusType: 'error',
            },
          ]
        : []),
      ...(props.user && props.resource.proposed && !isOwner.value && !props.resource.supporters?.includes(props.user.id)
        ? [
            {
              label: $t('resources.supportAction'),
              key: 'support',
              icon: renderIcon(StarIcon),
              action: () => emit('supportClick', props.resource),
              statusType: 'success',
            },
          ]
        : []),
      ...(props.user && props.resource.proposed && !isOwner.value  && !!props.resource.supporters?.includes(props.user.id)
        ? [
            {
              label: $t('resources.unsupportAction'),
              key: 'unsupport',
              icon: renderIcon(StarOffIcon),
              action: () => emit('unsupportClick', props.resource),
              statusType: 'error',
            },
          ]
        : []),
      ...(props.user?.isSuperuser && !props.resource.public && props.resource.proposed
        ? [
            {
              label: $t('resources.publishAction'),
              key: 'publish',
              disabled: !!props.resource.patchFor,
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
              disabled: !!props.resource.patchFor,
              icon: renderIcon(PublicOffIcon),
              action: () => emit('unpublishClick', props.resource),
              statusType: 'error',
            },
          ]
        : []),
      ...(!!props.resource.patchFor &&
      props.user &&
      isOwner.value
        ? [
            {
              label: $t('resources.reqPatchIntegration.action'),
              key: 'reqPatchtegration',
              icon: renderIcon(IntegratePatchIcon),
              disabled:
                resources.all
                  .find((r) => r.id === props.resource.patchFor)
                  ?.ownerIds.includes(props.user.id) ||
                !resources.all.find((r) => r.id === props.resource.patchFor)?.ownerIds.length,
              action: () => emit('reqPatchIntegrationClick', props.resource),
              statusType: 'success',
            },
          ]
        : []),
      ...(props.user?.isSuperuser || (isOwner.value && !props.resource.public && !props.resource.proposed)
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
          {{ $t('resources.viewContents') }}
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

    <n-alert v-if="props.user?.isSuperuser && resource.proposed" :show-icon="false" :type="resource.supporters?.length ? 'success' : 'error'" class="mb-lg">
      <n-flex align="center" class="b">
        <n-icon :component="resource.supporters?.length ? StarIcon : StarOffIcon" :color="resource.supporters?.length ? 'var(--success-color)' : 'var(--error-color)'" />
        <span>
        {{ $t('resources.proposed') + ', ' + $t('resources.supporters', { count: resource.supporters?.length ?? 0 }) + ' ...' }}
        </span>
      </n-flex>
      <user-display
        v-if="!!resource.supporters?.length && !!users"
        :user="users.filter(u => resource.supporters?.includes(u.id))"
        size="small"
        class="mt-lg"
      />
    </n-alert>

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
                :type="opt.statusType as ButtonType"
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
