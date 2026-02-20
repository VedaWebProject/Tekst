<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import type { components } from '@/api/schema';
import { dynInputCreateBtnProps } from '@/common';
import FormSection from '@/components/FormSection.vue';
import CodeEditor from '@/components/generic/CodeEditor.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { typeSpecificResourceConfigFormRules } from '@/forms/formRules';
import { javascript } from '@codemirror/lang-javascript';
import { NDynamicInput, NFormItem, NInput } from 'naive-ui';

defineProps<{ resource: AnyResourceRead }>();
const model = defineModel<components['schemas']['ContentTransformConfig']>({
  required: true,
});
</script>

<template>
  <form-section :title="$t('resources.settings.config.transformation.heading')" help-key="apiCallTransformation">
    <!-- TRANSFORM FN JS DEPENDENCIES -->
    <n-form-item :label="$t('resources.settings.config.transformation.deps')" class="parent-form-item">
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
            :label="$t('common.url')"
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
            top-offset
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
      :label="$t('resources.settings.config.transformation.js')"
      :rule="typeSpecificResourceConfigFormRules['apiCall'].js"
    >
    <div class="codemirror-container">
      <code class="translucent">{{'async function transform(this: {data: string, context: unknown}) {'}}</code>
      <code-editor v-model="model.js" :language="javascript" />
      <code class="translucent">{{'}'}}</code>
      </div>
    </n-form-item>
  </form-section>
</template>
