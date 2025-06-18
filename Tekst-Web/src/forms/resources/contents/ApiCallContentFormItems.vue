<script setup lang="ts">
import type { ApiCallContentCreate, ApiCallResourceRead } from '@/api';
import { dynInputCreateBtnProps } from '@/common';
import CodeEditor from '@/components/generic/CodeEditor.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { contentFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { json } from '@codemirror/lang-json';
import { NDynamicInput, NFormItem, NInput, NSelect } from 'naive-ui';
import { defaultContentModels } from './defaultContentModels';

defineProps<{
  resource: ApiCallResourceRead;
}>();

const model = defineModel<ApiCallContentCreate>({ required: true });

const methodOptions = ['GET', 'POST', 'QUERY', 'SEARCH'].map((m) => ({
  label: m,
  value: m,
}));
</script>

<template>
  <div>
    <n-form-item :show-label="false" path="calls">
      <n-dynamic-input
        v-model:value="model.calls"
        :min="1"
        :max="16"
        :show-sort-button="false"
        :create-button-props="dynInputCreateBtnProps"
        item-class="divided"
        @create="() => defaultContentModels.apiCall.calls[0] as ApiCallContentCreate['calls'][0]"
      >
        <template #default="{ value, index }">
          <div style="flex: 2">
            <!-- ENDPOINT URL -->
            <n-form-item
              :path="`calls.${index}.key`"
              :label="$t('common.key')"
              :rule="contentFormRules['apiCall'].key"
            >
              <n-input
                v-model:value="model.calls[index].key"
                type="text"
                :placeholder="$t('common.key')"
                @keydown.enter.prevent
              />
            </n-form-item>

            <!-- ENDPOINT URL -->
            <n-form-item
              :path="`calls.${index}.endpoint`"
              :label="$t('resources.types.apiCall.contentFields.endpoint')"
              :rule="contentFormRules['apiCall'].endpoint"
            >
              <n-input
                v-model:value="model.calls[index].endpoint"
                type="text"
                :placeholder="$t('resources.types.apiCall.contentFields.endpoint')"
                @keydown.enter.prevent
              />
            </n-form-item>

            <!-- HTTP METHOD -->
            <n-form-item
              :path="`calls.${index}.method`"
              :label="$t('resources.types.apiCall.contentFields.method')"
            >
              <n-select v-model:value="model.calls[index].method" :options="methodOptions" />
            </n-form-item>

            <!-- REQUEST BODY CONTENT TYPE -->
            <n-form-item
              :path="`calls.${index}.contentType`"
              :label="$t('resources.types.apiCall.contentFields.contentType')"
              :rule="contentFormRules['apiCall'].contentType"
            >
              <n-input
                v-model::value="model.calls[index].contentType"
                type="text"
                :placeholder="$t('resources.types.apiCall.contentFields.contentType')"
                :disabled="model.calls[index].method === 'GET'"
                @keydown.enter.prevent
              />
            </n-form-item>

            <!-- QUERY STRING (if method is GET) -->
            <n-form-item
              v-if="value.method === 'GET'"
              :label="$t('resources.types.apiCall.contentFields.queryString')"
              :path="`calls.${index}.query`"
              :rule="contentFormRules.apiCall.queryString"
            >
              <n-input
                v-model:value="model.calls[index].query"
                :placeholder="$t('resources.types.apiCall.contentFields.queryString')"
                @keydown.enter.prevent
              />
            </n-form-item>

            <!-- REQUEST BODY STRING -->
            <n-form-item
              v-else
              :label="$t('resources.types.apiCall.contentFields.body')"
              :path="`calls.${index}.query`"
              :rule="contentFormRules.apiCall.body"
            >
              <div class="codemirror-container">
                <code-editor v-model="model.calls[index].query" />
              </div>
            </n-form-item>
          </div>
        </template>
        <template #action="{ index, create, remove }">
          <dynamic-input-controls
            top-offset
            :movable="false"
            :insert-disabled="(model.calls.length || 0) >= 16"
            @remove="() => remove(index)"
            @insert="() => create(index)"
          />
        </template>
        <template #create-button-default>
          {{ $t('common.add') }}
        </template>
      </n-dynamic-input>
    </n-form-item>

    <!-- TRANSFORMATION CONTEXT DATA -->
    <n-form-item
      :label="$t('resources.types.apiCall.contentFields.transformContext')"
      path="transformContext"
      :rule="contentFormRules.apiCall.transformContext"
    >
      <div class="codemirror-container">
        <code-editor v-model="model.transformContext" :language="json" />
      </div>
    </n-form-item>
  </div>
</template>
