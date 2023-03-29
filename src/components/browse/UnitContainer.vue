<script setup lang="ts">
import { ref } from 'vue';
import { NSpin, NButton, NModal, NIcon } from 'naive-ui';
import MetadataDisplay from './MetadataDisplay.vue';
import InfoOutlined from '@vicons/material/InfoOutlined';
import ModalButtonFooter from '@/components/ModalButtonFooter.vue';

const props = defineProps<{
  title: string;
  layerType: string;
  loading?: boolean;
  active?: boolean;
  meta?: Record<string, string>;
  comment?: string;
}>();

const showMetaModal = ref(false);
</script>

<template>
  <div v-if="props.active" class="content-block" style="position: relative">
    <div class="unit-container-title">
      <div class="unit-container-title-heading">{{ props.title }}</div>
      <div>
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
      </div>
    </div>
    <slot></slot>
    <Transition>
      <n-spin v-show="props.loading" class="unit-container-loader" />
    </Transition>
  </div>

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
    <MetadataDisplay :data="props.meta" :layer-type="props.layerType" />
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
.unit-container-title {
  display: flex;
  flex-wrap: wrap-reverse;
  column-gap: 12px;
  row-gap: 0px;
  margin-bottom: 0.5rem;
}
.unit-container-title-heading {
  flex-grow: 2;
  color: var(--accent-color);
  font-size: var(--app-ui-font-size-small);
  font-weight: var(--app-ui-font-weight-normal);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.layer-comment {
  white-space: pre-wrap;
  font-weight: var(--app-ui-font-weight-light);
  font-size: var(--app-ui-font-size-medium);
}

.unit-container-loader {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: var(--content-bg-color);
  opacity: 0.9;
  border-radius: var(--app-ui-border-radius);
}

.unit-container-loader.v-enter-active,
.unit-container-loader.v-leave-active {
  transition: opacity 0.1s ease;
}

.unit-container-loader.v-enter-from,
.unit-container-loader.v-leave-to {
  opacity: 0;
}
</style>
