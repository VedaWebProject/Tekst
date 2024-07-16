<script setup lang="ts">
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { ref } from 'vue';
import { NButton } from 'naive-ui';
import { CommentIcon } from '@/icons';
import GenericModal from '@/components/generic/GenericModal.vue';
import type { AnyResourceRead } from '@/api';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';

defineProps<{
  resource: AnyResourceRead;
  small?: boolean;
}>();

const showModal = ref(false);
</script>

<template>
  <content-container-header-widget
    v-if="!!resource.contents?.[0]?.comment"
    :title="$t('general.comment')"
    :icon-component="CommentIcon"
    :small="small"
    @click="showModal = true"
  />

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
