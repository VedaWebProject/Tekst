<script setup lang="ts">
import type { AnyLayerRead, UserRead } from '@/api';
import { NEllipsis, NIcon, NListItem, NThing, NSpace, NButton } from 'naive-ui';
import { computed } from 'vue';
import LayerInfoWidget from '@/components/browse/widgets/LayerInfoWidget.vue';
import LayerPublicationStatus from '@/components/LayerPublicationStatus.vue';

import DeleteFilled from '@vicons/material/DeleteFilled';
import ModeEditFilled from '@vicons/material/ModeEditFilled';
import FlagFilled from '@vicons/material/FlagFilled';
import FlagOutlined from '@vicons/material/FlagOutlined';
import PublicFilled from '@vicons/material/PublicFilled';
import PublicOffFilled from '@vicons/material/PublicOffFilled';

const props = defineProps<{
  targetLayer: AnyLayerRead;
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
    (props.currentUser.isSuperuser || props.currentUser.id === props.targetLayer.ownerId) &&
    !props.targetLayer.public &&
    !props.targetLayer.proposed
);

const canPropose = computed(
  () =>
    props.currentUser &&
    (props.currentUser.isSuperuser || props.currentUser.id === props.targetLayer.ownerId) &&
    !props.targetLayer.public
);

const actionButtonProps = {
  quaternary: true,
  circle: true,
  focusable: false,
};
</script>

<template>
  <n-list-item>
    <n-thing :title="targetLayer.title" content-style="margin-top: 8px">
      <template #description>
        <div style="font-size: var(--app-ui-font-size-small)">
          <div v-if="targetLayer.description" style="font-weight: var(--app-ui-font-weight-normal)">
            {{ targetLayer.description }}
          </div>
          <div
            v-if="targetLayer.comment"
            :style="targetLayer.description ? 'margin-top: .25rem' : ''"
          >
            <n-ellipsis
              expand-trigger="click"
              :tooltip="false"
              :line-clamp="2"
              style="opacity: 0.75"
            >
              {{ $t('models.layer.comment') }}: {{ targetLayer.comment }}
            </n-ellipsis>
          </div>
        </div>
      </template>
      <template #header-extra>
        <n-space>
          <!-- propose -->
          <n-button
            v-if="canPropose && !targetLayer.proposed"
            v-bind="actionButtonProps"
            :title="$t('dataLayers.proposeAction')"
            @click="$emit('proposeClick', targetLayer)"
          >
            <template #icon>
              <n-icon :component="FlagFilled" />
            </template>
          </n-button>
          <!-- withdraw proposal -->
          <n-button
            v-if="canPropose && targetLayer.proposed"
            v-bind="actionButtonProps"
            :title="$t('dataLayers.unproposeAction')"
            @click="$emit('unproposeClick', targetLayer)"
          >
            <template #icon>
              <n-icon :component="FlagOutlined" />
            </template>
          </n-button>
          <!-- publish -->
          <n-button
            v-if="currentUser?.isSuperuser && targetLayer.proposed"
            v-bind="actionButtonProps"
            :title="$t('dataLayers.publishAction')"
            @click="$emit('publishClick', targetLayer)"
          >
            <template #icon>
              <n-icon :component="PublicFilled" />
            </template>
          </n-button>
          <!-- withdraw publication -->
          <n-button
            v-if="currentUser?.isSuperuser && targetLayer.public"
            v-bind="actionButtonProps"
            :title="$t('dataLayers.unpublishAction')"
            @click="$emit('unpublishClick', targetLayer)"
          >
            <template #icon>
              <n-icon :component="PublicOffFilled" />
            </template>
          </n-button>
          <!-- edit -->
          <n-button
            v-if="targetLayer.writable"
            v-bind="actionButtonProps"
            :title="$t('general.editAction')"
            @click="$emit('editClick', targetLayer)"
          >
            <template #icon>
              <n-icon :component="ModeEditFilled" />
            </template>
          </n-button>
          <!-- delete -->
          <n-button
            v-if="canDelete"
            v-bind="actionButtonProps"
            :title="$t('general.deleteAction')"
            @click="$emit('deleteClick', targetLayer)"
          >
            <template #icon>
              <n-icon :component="DeleteFilled" />
            </template>
          </n-button>
          <!-- layer info -->
          <LayerInfoWidget :layer="targetLayer" />
        </n-space>
      </template>
      <LayerPublicationStatus :layer="targetLayer" />
    </n-thing>
  </n-list-item>
</template>
