<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NModal } from 'naive-ui';
import MetadataDisplay from '@/components/browse/MetadataDisplay.vue';
import ModalButtonFooter from '@/components/ModalButtonFooter.vue';
import InfoOutlined from '@vicons/material/InfoOutlined';
import UnitContainerHeaderWidget from '@/components/browse/UnitContainerHeaderWidget.vue';

const props = defineProps<{
  title: string;
  meta?: Record<string, string>;
  comment?: string;
}>();

const showMetaModal = ref(false);
</script>

<template>
  <UnitContainerHeaderWidget
    :title="$t('meta.metadata')"
    :iconComponent="InfoOutlined"
    @click="showMetaModal = true"
  />

  <n-modal
    v-model:show="showMetaModal"
    preset="card"
    class="textrig-modal"
    size="large"
    :bordered="false"
    :auto-focus="false"
    :closable="false"
    to="#app-container"
  >
    <h2>{{ props.title }}: {{ $t('meta.metadata') }}</h2>
    <MetadataDisplay :data="props.meta" />
    <template v-if="props.comment">
      <h3>{{ $t('meta.comment') }}</h3>
      <div class="layer-comment">
        {{ props.comment }}
      </div>
    </template>
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
