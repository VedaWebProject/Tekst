<script setup lang="ts">
import { PromptTemplatePromise } from '@/templatePromises';
import { NButton, NModal, NInput, NFormItem } from 'naive-ui';
import ButtonFooter from './ButtonFooter.vue';
import { ref } from 'vue';

const value = ref('');
</script>

<template>
  <PromptTemplatePromise v-slot="{ args, resolve, reject }">
    <n-modal
      :show="true"
      preset="card"
      class="tekst-modal"
      size="medium"
      :bordered="false"
      :closable="false"
      to="#app-container"
      :title="args[0]"
      embedded
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
      <ButtonFooter>
        <n-button secondary @click="reject(null)">
          {{ $t('general.cancelAction') }}
        </n-button>
        <n-button type="primary" @click="resolve(value)">
          {{ $t('general.okAction') }}
        </n-button>
      </ButtonFooter>
    </n-modal>
  </PromptTemplatePromise>
</template>
