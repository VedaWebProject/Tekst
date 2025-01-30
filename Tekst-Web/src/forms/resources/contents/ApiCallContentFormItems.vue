<script setup lang="ts">
import type { ApiCallContentCreate, ApiCallResourceRead } from '@/api';
import { contentFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { json } from '@codemirror/lang-json';
import { NFormItem, NInput } from 'naive-ui';
import { Codemirror } from 'vue-codemirror';

defineProps<{
  resource: ApiCallResourceRead;
}>();

const model = defineModel<ApiCallContentCreate>({ required: true });
const extraEditorExtensions = [json()];
</script>

<template>
  <!-- QUERY STRING (if method is GET) -->
  <n-form-item
    v-if="resource.config.apiCall.method === 'GET'"
    :label="$t('resources.types.apiCall.contentFields.queryString')"
    path="query"
    :rule="contentFormRules.apiCall.queryString"
  >
    <n-input
      v-model:value="model.query"
      :placeholder="$t('resources.types.apiCall.contentFields.queryString')"
      @keydown.enter.prevent
    />
  </n-form-item>

  <!-- REQUEST BODY STRING -->
  <n-form-item
    v-else
    :label="$t('resources.types.apiCall.contentFields.body')"
    path="query"
    :rule="contentFormRules.apiCall.body"
  >
    <div class="codemirror-container">
      <codemirror
        v-model="model.query"
        :style="{ height: '400px', fontSize: 'var(--font-size-small)' }"
        :indent-with-tab="true"
        :tab-size="2"
      />
    </div>
  </n-form-item>

  <!-- TRANSFORMATION EXTRA DATA -->
  <n-form-item
    :label="$t('resources.types.apiCall.contentFields.extra')"
    path="extra"
    :rule="contentFormRules.apiCall.extra"
  >
    <div class="codemirror-container">
      <codemirror
        v-model="model.extra"
        :style="{ height: '400px', fontSize: 'var(--font-size-small)' }"
        :indent-with-tab="true"
        :tab-size="2"
        :extensions="extraEditorExtensions"
      />
    </div>
  </n-form-item>
</template>
