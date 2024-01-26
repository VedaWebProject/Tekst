<script setup lang="ts">
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { ref } from 'vue';
import { NButton } from 'naive-ui';
import { CommentIcon } from '@/icons';
import GenericModal from '../generic/GenericModal.vue';
import type { AnyResourceRead } from '@/api';
import ButtonShelf from '../generic/ButtonShelf.vue';

defineProps<{
  resource: AnyResourceRead;
}>();

const showModal = ref(false);
</script>

<template>
  <ContentContainerHeaderWidget
    v-if="!!resource.contents?.[0]?.comment"
    :title="$t('browse.contents.widgets.contentComment.title')"
    :icon-component="CommentIcon"
    @click="showModal = true"
  />

  <GenericModal
    v-model:show="showModal"
    width="wide"
    :title="$t('browse.contents.widgets.contentComment.title')"
    :icon="CommentIcon"
  >
    <p v-if="resource.contents?.[0]?.comment" style="white-space: pre-wrap">
      {{ resource.contents[0].comment }}
    </p>
    <ButtonShelf top-gap>
      <n-button type="primary" @click="showModal = false">
        {{ $t('general.closeAction') }}
      </n-button>
    </ButtonShelf>
  </GenericModal>
</template>
