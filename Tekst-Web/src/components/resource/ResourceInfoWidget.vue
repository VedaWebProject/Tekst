<script setup lang="ts">
import { type AnyResourceRead } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import CopyToClipboardButton from '@/components/generic/CopyToClipboardButton.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import ResourceInfoContent from '@/components/resource/ResourceInfoContent.vue';
import ResourceInfoTags from '@/components/resource/ResourceInfoTags.vue';
import env from '@/env';
import { InfoIcon, ResourceIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { NButton, NFlex } from 'naive-ui';
import { computed, ref } from 'vue';

const props = defineProps<{
  resource: AnyResourceRead;
  full?: boolean;
}>();

const emit = defineEmits(['done']);

const state = useStateStore();

const title = computed(() => pickTranslation(props.resource.title, state.locale));
const showInfoModal = ref(false);

const resInfoUrl = computed(
  () =>
    `${origin}${env.WEB_PATH_STRIPPED}/texts/${state.text?.slug || '???'}/resources#id=${props.resource.id}`
);
</script>

<template>
  <content-container-header-widget
    v-if="!$slots.default"
    :full="full"
    :title="$t('common.information')"
    :icon-component="InfoIcon"
    @click="
      () => {
        showInfoModal = true;
        emit('done');
      }
    "
  />

  <template v-else>
    <div
      style="padding: 0; margin: 0; line-height: 0"
      @click="
        () => {
          showInfoModal = true;
          emit('done');
        }
      "
    >
      <slot></slot>
    </div>
  </template>

  <generic-modal v-model:show="showInfoModal" :title="title" :icon="ResourceIcon" width="wide">
    <n-flex justify="space-between" align="center" class="mb-lg" style="flex-wrap: wrap-reverse">
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
      <resource-info-tags :resource="resource" />
    </n-flex>
    <resource-info-content :resource="resource" />
    <button-shelf class="mt-lg">
      <n-button type="primary" @click="() => (showInfoModal = false)">
        {{ $t('common.close') }}
      </n-button>
    </button-shelf>
  </generic-modal>
</template>
