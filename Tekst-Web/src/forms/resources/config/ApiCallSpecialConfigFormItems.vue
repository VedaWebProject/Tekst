<script setup lang="ts">
import type { ApiCallResourceRead } from '@/api';
import type { components } from '@/api/schema';
import { dynInputCreateBtnProps } from '@/common';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import CodeEditor from '@/components/generic/CodeEditor.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { typeSpecificResourceConfigFormRules } from '@/forms/formRules';
import { javascript } from '@codemirror/lang-javascript';
import { NDynamicInput, NFlex, NFormItem, NInput, NSelect } from 'naive-ui';

defineProps<{ resource: ApiCallResourceRead }>();

const model = defineModel<components['schemas']['ApiCallSpecialConfig']>({
  required: true,
});

const methodOptions = ['GET', 'POST', 'QUERY', 'SEARCH'].map((m) => ({
  label: m,
  value: m,
}));
</script>

<template>
  <form-section-heading :label="$t('resources.settings.config.apiCall.headingApiRequest')" />

  <!-- ENDPOINT URL -->
  <n-form-item
    path="config.apiCall.endpoint"
    :label="$t('resources.settings.config.apiCall.endpoint')"
    :rule="typeSpecificResourceConfigFormRules['apiCall'].endpoint"
  >
    <n-input
      v-model:value="model.endpoint"
      type="text"
      :placeholder="$t('resources.settings.config.apiCall.endpoint')"
      @keydown.enter.prevent
    />
  </n-form-item>

  <!-- HTTP METHOD -->
  <n-form-item path="config.apiCall.method" :label="$t('resources.settings.config.apiCall.method')">
    <n-select v-model:value="model.method" :options="methodOptions" />
  </n-form-item>

  <!-- REQUEST BODY CONTENT TYPE -->
  <n-form-item
    path="config.apiCall.contentType"
    :label="$t('resources.settings.config.apiCall.contentType')"
    :rule="typeSpecificResourceConfigFormRules['apiCall'].contentType"
  >
    <n-input
      v-model::value="model.contentType"
      type="text"
      :placeholder="$t('resources.settings.config.apiCall.contentType')"
      :disabled="model.method === 'GET'"
      @keydown.enter.prevent
    />
  </n-form-item>

  <form-section-heading
    :label="$t('resources.settings.config.apiCall.headingResponseTransformation')"
  />

  <!-- TRANSFORM FN JS DEPENDENCIES -->
  <n-form-item>
    <template #label>
      <n-flex align="center">
        {{ $t('resources.settings.config.apiCall.transformDeps') }}
        <help-button-widget help-key="apiCallTransformDeps" />
      </n-flex>
    </template>
    <n-dynamic-input
      v-model::value="model.transformDeps"
      show-sort-button
      :min="0"
      :max="32"
      :create-button-props="dynInputCreateBtnProps"
      @create="() => ''"
    >
      <template #default="{ index }">
        <n-form-item
          ignore-path-change
          :show-label="false"
          :path="`config.apiCall.transformDeps[${index}]`"
          :rule="typeSpecificResourceConfigFormRules.apiCall.transformDep"
          style="flex: 2"
        >
          <n-input
            v-model:value="model.transformDeps[index]"
            :placeholder="$t('general.url')"
            @keydown.enter.prevent
          />
        </n-form-item>
      </template>
      <template #action="{ index, create, remove }">
        <dynamic-input-controls
          :movable="false"
          :insert-disabled="(model.transformDeps.length || 0) >= 32"
          @remove="() => remove(index)"
          @insert="() => create(index)"
        />
      </template>
      <template #create-button-default>
        {{ $t('general.addAction') }}
      </template>
    </n-dynamic-input>
  </n-form-item>

  <!-- RESPONSE TRANSFORM JS FN BODY -->
  <n-form-item
    path="config.apiCall.transformJs"
    :rule="typeSpecificResourceConfigFormRules['apiCall'].transformJs"
  >
    <template #label>
      <n-flex align="center">
        {{ $t('resources.settings.config.apiCall.transformJs') }}
        <help-button-widget help-key="apiCallTransformJs" />
      </n-flex>
    </template>
    <div class="codemirror-container">
      <code-editor v-model="model.transformJs" :language="javascript" />
    </div>
  </n-form-item>
</template>
