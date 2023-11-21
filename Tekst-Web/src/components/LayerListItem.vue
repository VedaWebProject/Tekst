<script setup lang="ts">
import type { AnyLayerReadFull, UserRead } from '@/api';
import { NIcon, NListItem, NThing, NSpace, NButton } from 'naive-ui';
import { computed } from 'vue';
import LayerInfoWidget from '@/components/browse/widgets/LayerInfoWidget.vue';
import LayerPublicationStatus from '@/components/LayerPublicationStatus.vue';

import DeleteFilled from '@vicons/material/DeleteFilled';
import ModeEditFilled from '@vicons/material/ModeEditFilled';
import StarHalfOutlined from '@vicons/material/StarHalfOutlined';
import PublicFilled from '@vicons/material/PublicFilled';
import PublicOffFilled from '@vicons/material/PublicOffFilled';

const props = defineProps<{
  targetLayer: AnyLayerReadFull;
  currentUser?: UserRead;
}>();

defineEmits(['deleteClick']);

const canDelete = computed(
  () =>
    props.currentUser &&
    (props.currentUser.isSuperuser || props.currentUser.id === props.targetLayer.ownerId)
);

const canPropose = computed(
  () =>
    props.currentUser &&
    (props.currentUser.isSuperuser || props.currentUser.id === props.targetLayer.ownerId) &&
    !props.targetLayer.public &&
    !props.targetLayer.proposed
);
</script>

<template>
  <n-list-item>
    <n-thing :title="targetLayer.title" content-style="margin-top: 8px">
      <template #description>
        <div style="opacity: 0.75; font-size: var(--app-ui-font-size-small)">
          <div v-if="targetLayer.description">
            {{ targetLayer.description }}
          </div>
          <div v-if="targetLayer.comment">
            {{ $t('models.layer.comment') }}: {{ targetLayer.comment }}
          </div>
        </div>
      </template>
      <template #header-extra>
        <n-space>
          <!-- propose -->
          <n-button v-if="canPropose" secondary :title="$t('dataLayers.proposeAction')">
            <template #icon>
              <n-icon :component="StarHalfOutlined" />
            </template>
          </n-button>
          <!-- make public -->
          <n-button
            v-if="currentUser?.isSuperuser && targetLayer.proposed"
            secondary
            :title="$t('dataLayers.makePublicAction')"
          >
            <template #icon>
              <n-icon :component="PublicFilled" />
            </template>
          </n-button>
          <!-- make private -->
          <n-button
            v-if="currentUser?.isSuperuser && targetLayer.public"
            secondary
            :title="$t('dataLayers.makePrivateAction')"
          >
            <template #icon>
              <n-icon :component="PublicOffFilled" />
            </template>
          </n-button>
          <!-- edit -->
          <n-button v-if="targetLayer.writable" secondary :title="$t('general.editAction')">
            <template #icon>
              <n-icon :component="ModeEditFilled" />
            </template>
          </n-button>
          <!-- delete -->
          <n-button v-if="canDelete" secondary :title="$t('general.deleteAction')">
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
