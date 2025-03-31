<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import type { components } from '@/api/schema';
import { dynInputCreateBtnProps } from '@/common';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import CodeEditor from '@/components/generic/CodeEditor.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { typeSpecificResourceConfigFormRules } from '@/forms/formRules';
import { javascript } from '@codemirror/lang-javascript';
import { NDynamicInput, NFlex, NFormItem, NInput } from 'naive-ui';

defineProps<{ resource: AnyResourceRead }>();
const model = defineModel<components['schemas']['ContentTransformConfig']>({
  required: true,
});
</script>

<template>
  <form-section-heading :label="$t('resources.settings.config.transformation.heading')" />

  <!-- TRANSFORM FN JS DEPENDENCIES -->
  <n-form-item>
    <template #label>
      <n-flex align="center">
        {{ $t('resources.settings.config.transformation.deps') }}
        <help-button-widget help-key="apiCallTransformDeps" />
      </n-flex>
    </template>
    <n-dynamic-input
      v-model:value="model.deps"
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
          :path="`config.special.transform.deps[${index}]`"
          :rule="typeSpecificResourceConfigFormRules.apiCall.dep"
          style="flex: 2"
        >
          <n-input
            v-model:value="model.deps[index]"
            :placeholder="$t('common.url')"
            @keydown.enter.prevent
          />
        </n-form-item>
      </template>
      <template #action="{ index, create, remove }">
        <dynamic-input-controls
          :movable="false"
          :insert-disabled="(model.deps.length || 0) >= 32"
          @remove="() => remove(index)"
          @insert="() => create(index)"
        />
      </template>
      <template #create-button-default>
        {{ $t('common.add') }}
      </template>
    </n-dynamic-input>
  </n-form-item>

  <!-- RESPONSE TRANSFORM JS FN BODY -->
  <n-form-item
    path="config.special.transform.js"
    :rule="typeSpecificResourceConfigFormRules['apiCall'].js"
  >
    <template #label>
      <n-flex align="center">
        {{ $t('resources.settings.config.transformation.js') }}
        <help-button-widget help-key="apiCallTransformJs" />
      </n-flex>
    </template>
    <div class="codemirror-container">
      <code-editor v-model="model.js" :language="javascript" />
    </div>
  </n-form-item>
</template>
