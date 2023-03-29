<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NModal, NIcon } from 'naive-ui';
import MetadataDisplay from './MetadataDisplay.vue';
import ModalButtonFooter from '@/components/ModalButtonFooter.vue';
import InfoOutlined from '@vicons/material/InfoOutlined';

const props = defineProps<{
  title: string;
  meta?: Record<string, string>;
  comment?: string;
}>();

const showMetaModal = ref(false);
</script>

<template>
  <n-button
    v-if="props.meta || props.comment"
    quaternary
    circle
    @click="showMetaModal = true"
    :focusable="false"
    :title="$t('meta.metadata')"
  >
    <template #icon>
      <n-icon size="22px" :component="InfoOutlined" />
    </template>
  </n-button>

  <n-modal
    v-model:show="showMetaModal"
    preset="card"
    class="textrig-modal"
    size="large"
    :bordered="false"
    :auto-focus="false"
    :closable="false"
  >
    <h2>{{ props.title }}: {{ $t('meta.metadata') }}</h2>
    <MetadataDisplay :data="props.meta" />
    <h3 v-if="props.comment">{{ $t('meta.comment') }}</h3>
    <div v-if="props.comment" class="layer-comment">
      {{ props.comment }}
    </div>
    <ModalButtonFooter>
      <n-button type="primary" @click="() => (showMetaModal = false)">
        {{ $t('general.closeAction') }}
      </n-button>
    </ModalButtonFooter>
  </n-modal>
</template>

<style scoped>
.layer-comment {
  white-space: pre-wrap;
  font-weight: var(--app-ui-font-weight-light);
  font-size: var(--app-ui-font-size-medium);
}
</style>
