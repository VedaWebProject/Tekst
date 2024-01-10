<script setup lang="ts">
import { PromptTemplatePromise } from '@/templatePromises';
import { NButton, NInput, NFormItem } from 'naive-ui';
import ButtonShelf from './ButtonShelf.vue';
import { ref } from 'vue';
import GenericModal from './GenericModal.vue';

import KeyboardOutlined from '@vicons/material/KeyboardOutlined';

const value = ref('');
</script>

<template>
  <PromptTemplatePromise v-slot="{ args, resolve, reject }">
    <GenericModal
      show
      :title="args[0]"
      :icon="KeyboardOutlined"
      :closable="false"
      @close="reject(null)"
      @mask-click="reject(null)"
      @vue:mounted="value = args[2] || ''"
      @esc="reject(null)"
    >
      <n-form-item :label="args[1]">
        <n-input
          v-model:value="value"
          type="text"
          placeholder=""
          @keydown.enter="
            (e) => {
              e.preventDefault();
              e.stopPropagation();
              resolve(value);
            }
          "
        />
      </n-form-item>
      <ButtonShelf top-gap>
        <n-button secondary @click="reject(null)">
          {{ $t('general.cancelAction') }}
        </n-button>
        <n-button type="primary" @click="resolve(value)">
          {{ $t('general.okAction') }}
        </n-button>
      </ButtonShelf>
    </GenericModal>
  </PromptTemplatePromise>
</template>
