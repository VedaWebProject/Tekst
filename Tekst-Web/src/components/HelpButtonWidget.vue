<script setup lang="ts">
import { ref } from 'vue';
import { NModal, NButton, NIcon } from 'naive-ui';

import QuestionMarkFilled from '@vicons/material/QuestionMarkFilled';
import type { Size } from 'naive-ui/es/button/src/interface';

withDefaults(
  defineProps<{
    size?: Size;
  }>(),
  { size: 'tiny' }
);

const showModal = ref(false);
const title = ref('...');
const content = ref('...');
</script>

<template>
  <div style="display: inline-table; height: 100%">
    <n-button
      secondary
      circle
      color="var(--accent-color)"
      :size="size"
      :title="$t('help.helpButtonTitle')"
      style="vertical-align: super"
      @click="showModal = true"
    >
      <template #icon>
        <n-icon :component="QuestionMarkFilled" />
      </template>
    </n-button>
  </div>

  <n-modal
    v-model:show="showModal"
    preset="card"
    class="tekst-modal"
    size="large"
    :bordered="false"
    :auto-focus="false"
    :closable="true"
    to="#app-container"
    :title="title"
    embedded
  >
    {{ content }}
  </n-modal>
</template>
