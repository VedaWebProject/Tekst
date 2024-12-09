<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import { CommentIcon } from '@/icons';
import { NBadge, NButton } from 'naive-ui';
import { ref } from 'vue';

defineProps<{
  resource: AnyResourceRead;
  full?: boolean;
}>();

const emit = defineEmits(['done']);

const showModal = ref(false);
</script>

<template>
  <n-badge v-if="!!resource.contents?.[0]?.comment" show dot :offset="[-5, 10]">
    <content-container-header-widget
      :full="full"
      :title="$t('general.comment')"
      :icon-component="CommentIcon"
      @click="
        () => {
          showModal = true;
          emit('done');
        }
      "
    />
  </n-badge>

  <generic-modal
    v-model:show="showModal"
    width="wide"
    :title="$t('general.comment')"
    :icon="CommentIcon"
  >
    <p v-if="resource.contents?.[0]?.comment" style="white-space: pre-wrap">
      {{ resource.contents[0].comment }}
    </p>
    <button-shelf top-gap>
      <n-button type="primary" @click="showModal = false">
        {{ $t('general.closeAction') }}
      </n-button>
    </button-shelf>
  </generic-modal>
</template>
