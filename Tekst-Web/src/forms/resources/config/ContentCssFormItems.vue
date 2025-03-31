<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import type { components } from '@/api/schema';
import { dynInputCreateBtnProps } from '@/common';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { contentCssConfigFormRules } from '@/forms/formRules';
import { all as knownCssProperties } from 'known-css-properties';
import { NDynamicInput, NFlex, NFormItem, NInput, NSelect } from 'naive-ui';

defineProps<{ resource: AnyResourceRead }>();
const model = defineModel<components['schemas']['ContentCssProperties']>({
  required: true,
});

const propertyOptions = knownCssProperties.map((p) => ({ label: p, value: p }));
</script>

<template>
  <form-section-heading
    :label="$t('resources.settings.config.contentCss.heading')"
    help-key="contentCssConfig"
  />
  <n-form-item :show-label="false">
    <n-dynamic-input
      v-model:value="model"
      :min="0"
      :max="64"
      :show-sort-button="false"
      :create-button-props="dynInputCreateBtnProps"
      @create="() => ({ prop: undefined, value: undefined })"
    >
      <template #default="{ value, index }">
        <n-flex align="flex-start" wrap style="flex: 2">
          <!-- PROPERTY NAME -->
          <n-form-item
            ignore-path-change
            :label="$t('resources.settings.config.contentCss.prop')"
            :path="`config.special.contentCss[${index}].prop`"
            :rule="contentCssConfigFormRules.prop"
            style="flex: 1 200px"
          >
            <n-select
              v-model:value="value.prop"
              filterable
              :options="propertyOptions"
              :placeholder="$t('common.select')"
            />
          </n-form-item>
          <!-- PROPERTY VALUE -->
          <n-form-item
            ignore-path-change
            :label="$t('common.value')"
            :path="`config.special.contentCss[${index}].value`"
            :rule="contentCssConfigFormRules.value"
            style="flex: 1 200px"
          >
            <n-input
              v-model:value="value.value"
              :placeholder="$t('common.value')"
              @keydown.enter.prevent
            />
          </n-form-item>
        </n-flex>
      </template>
      <template #action="{ index, create, remove }">
        <dynamic-input-controls
          top-offset
          :movable="false"
          :insert-disabled="(model.length || 0) >= 64"
          @remove="() => remove(index)"
          @insert="() => create(index)"
        />
      </template>
      <template #create-button-default>
        {{ $t('common.add') }}
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>
