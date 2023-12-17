<script setup lang="ts">
import type { AnyResourceRead, UserRead } from '@/api';
import { NEllipsis, NIcon, NListItem, NThing, NSpace, NButton } from 'naive-ui';
import { computed } from 'vue';
import ResourceInfoWidget from '@/components/browse/widgets/ResourceInfoWidget.vue';
import ResourcePublicationStatus from '@/components/ResourcePublicationStatus.vue';

import DeleteFilled from '@vicons/material/DeleteFilled';
import SettingsFilled from '@vicons/material/SettingsFilled';
import FlagFilled from '@vicons/material/FlagFilled';
import FlagOutlined from '@vicons/material/FlagOutlined';
import PublicFilled from '@vicons/material/PublicFilled';
import PublicOffFilled from '@vicons/material/PublicOffFilled';
import TranslationDisplay from './TranslationDisplay.vue';

const props = defineProps<{
  targetResource: AnyResourceRead;
  currentUser?: UserRead;
}>();

defineEmits([
  'proposeClick',
  'unproposeClick',
  'publishClick',
  'unpublishClick',
  'editClick',
  'deleteClick',
]);

const canDelete = computed(
  () =>
    props.currentUser &&
    (props.currentUser.isSuperuser || props.currentUser.id === props.targetResource.ownerId) &&
    !props.targetResource.public &&
    !props.targetResource.proposed
);

const canPropose = computed(
  () =>
    props.currentUser &&
    (props.currentUser.isSuperuser || props.currentUser.id === props.targetResource.ownerId) &&
    !props.targetResource.public
);

const actionButtonProps = {
  quaternary: true,
  circle: true,
  focusable: false,
};
</script>

<template>
  <n-list-item class="resource-list-item">
    <n-thing :title="targetResource.title" content-style="margin-top: 8px">
      <template #description>
        <div style="font-size: var(--app-ui-font-size-small)">
          <div v-if="targetResource.description?.length">
            <TranslationDisplay :value="targetResource.description" />
          </div>
          <div
            v-if="targetResource.comment?.length"
            :style="targetResource.description ? 'margin-top: .25rem' : ''"
          >
            <n-ellipsis
              expand-trigger="click"
              :tooltip="false"
              :line-clamp="2"
              style="opacity: 0.75"
            >
              {{ $t('models.resource.comment') }}:
              <TranslationDisplay :value="targetResource.comment" />
            </n-ellipsis>
          </div>
        </div>
      </template>
      <template #header-extra>
        <n-space>
          <!-- propose -->
          <n-button
            v-if="canPropose && !targetResource.proposed"
            v-bind="actionButtonProps"
            :title="$t('resources.proposeAction')"
            @click="$emit('proposeClick', targetResource)"
          >
            <template #icon>
              <n-icon :component="FlagFilled" />
            </template>
          </n-button>
          <!-- withdraw proposal -->
          <n-button
            v-if="canPropose && targetResource.proposed"
            v-bind="actionButtonProps"
            :title="$t('resources.unproposeAction')"
            @click="$emit('unproposeClick', targetResource)"
          >
            <template #icon>
              <n-icon :component="FlagOutlined" />
            </template>
          </n-button>
          <!-- publish -->
          <n-button
            v-if="currentUser?.isSuperuser && targetResource.proposed && !targetResource.public"
            v-bind="actionButtonProps"
            :title="$t('resources.publishAction')"
            @click="$emit('publishClick', targetResource)"
          >
            <template #icon>
              <n-icon :component="PublicFilled" />
            </template>
          </n-button>
          <!-- withdraw publication -->
          <n-button
            v-if="currentUser?.isSuperuser && targetResource.public"
            v-bind="actionButtonProps"
            :title="$t('resources.unpublishAction')"
            @click="$emit('unpublishClick', targetResource)"
          >
            <template #icon>
              <n-icon :component="PublicOffFilled" />
            </template>
          </n-button>
          <!-- edit -->
          <n-button
            :disabled="!targetResource.writable"
            v-bind="actionButtonProps"
            :title="$t('general.editAction')"
            @click="$emit('editClick', targetResource)"
          >
            <template #icon>
              <n-icon :component="SettingsFilled" />
            </template>
          </n-button>
          <!-- delete -->
          <n-button
            :disabled="!canDelete"
            v-bind="actionButtonProps"
            :title="$t('general.deleteAction')"
            @click="$emit('deleteClick', targetResource)"
          >
            <template #icon>
              <n-icon :component="DeleteFilled" />
            </template>
          </n-button>
          <!-- resource info -->
          <ResourceInfoWidget :resource="targetResource" />
        </n-space>
      </template>
      <ResourcePublicationStatus :resource="targetResource" size="small" />
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
