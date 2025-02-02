<script setup lang="ts">
import type { components } from '@/api/schema';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { typeSpecificResourceConfigFormRules } from '@/forms/formRules';
import { javascript } from '@codemirror/lang-javascript';
import { NDynamicInput, NFlex, NFormItem, NInput, NSelect } from 'naive-ui';
import { Codemirror } from 'vue-codemirror';

const model = defineModel<components['schemas']['ApiCallResourceConfig']['apiCall']>({
  required: true,
});

const codeEditorExtensions = [javascript()];

const methodOptions = ['GET', 'POST', 'QUERY', 'SEARCH'].map((m) => ({
  label: m,
  value: m,
}));

function handleUpdate(field: string, value: unknown) {
  model.value = {
    ...model.value,
    [field]: value,
  };
}
</script>

<template>
  <!-- ENDPOINT URL -->
  <n-form-item
    path="config.apiCall.endpoint"
    :label="$t('resources.settings.config.apiCall.endpoint')"
    :rule="typeSpecificResourceConfigFormRules['apiCall'].endpoint"
  >
    <n-input
      :value="model.endpoint"
      type="text"
      :placeholder="$t('resources.settings.config.apiCall.endpoint')"
      @keydown.enter.prevent
      @update:value="(v) => handleUpdate('endpoint', v)"
    />
  </n-form-item>

  <!-- ENDPOINT URL -->
  <n-form-item path="config.apiCall.method" :label="$t('resources.settings.config.apiCall.method')">
    <n-select
      :value="model.method"
      :options="methodOptions"
      @update:value="(v) => handleUpdate('method', v)"
    />
  </n-form-item>

  <!-- REQUEST BODY CONTENT TYPE -->
  <n-form-item
    path="config.apiCall.contentType"
    :label="$t('resources.settings.config.apiCall.contentType')"
    :rule="typeSpecificResourceConfigFormRules['apiCall'].contentType"
  >
    <n-input
      :value="model.contentType"
      type="text"
      :placeholder="$t('resources.settings.config.apiCall.contentType')"
      :disabled="model.method === 'GET'"
      @keydown.enter.prevent
      @update:value="(v) => handleUpdate('contentType', v)"
    />
  </n-form-item>

  <!-- TRANSFORM FN JS DEPENDENCIES -->
  <n-form-item>
    <template #label>
      <n-flex align="center">
        {{ $t('resources.settings.config.apiCall.transformDeps') }}
        <help-button-widget help-key="apiCallTransformDeps" />
      </n-flex>
    </template>
    <n-dynamic-input
      :value="model.transformDeps"
      show-sort-button
      :min="0"
      :max="32"
      @create="() => ''"
      @update:value="(v) => handleUpdate('transformDeps', v)"
    >
      <template #default="{ index }">
        <n-form-item
          ignore-path-change
          :show-label="false"
          :path="`config.apiCall.transformDeps[${index}]`"
          :rule="typeSpecificResourceConfigFormRules.apiCall.transformDep"
          style="flex-grow: 2"
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
      <codemirror
        :model-value="model.transformJs"
        :style="{ height: '400px', fontSize: 'var(--font-size-small)' }"
        class="codemirror-container"
        :indent-with-tab="true"
        :tab-size="2"
        :extensions="codeEditorExtensions"
        @update:model-value="(v) => handleUpdate('transformJs', v)"
      />
    </div>
  </n-form-item>
</template>
