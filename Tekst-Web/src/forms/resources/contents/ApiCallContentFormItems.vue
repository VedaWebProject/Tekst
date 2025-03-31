<script setup lang="ts">
import type { ApiCallContentCreate, ApiCallResourceRead } from '@/api';
import CodeEditor from '@/components/generic/CodeEditor.vue';
import { contentFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { json } from '@codemirror/lang-json';
import { NFormItem, NInput } from 'naive-ui';

defineProps<{
  resource: ApiCallResourceRead;
}>();

const model = defineModel<ApiCallContentCreate>({ required: true });
</script>

<template>
  <!-- QUERY STRING (if method is GET) -->
  <n-form-item
    v-if="resource.config.special.apiCall.method === 'GET'"
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
      <code-editor v-model="model.query" />
    </div>
  </n-form-item>

  <!-- TRANSFORMATION EXTRA DATA -->
  <n-form-item
    :label="$t('resources.types.apiCall.contentFields.transformContext')"
    path="extra"
    :rule="contentFormRules.apiCall.extra"
  >
    <div class="codemirror-container">
      <code-editor v-model="model.transformContext" :language="json" />
    </div>
  </n-form-item>
</template>
