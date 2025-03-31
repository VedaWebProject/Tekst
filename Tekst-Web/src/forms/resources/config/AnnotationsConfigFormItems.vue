<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import type { components } from '@/api/schema';
import { dynInputCreateBtnProps } from '@/common';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { typeSpecificResourceConfigFormRules } from '@/forms/formRules';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import { NDynamicInput, NFlex, NFormItem, NInput } from 'naive-ui';

defineProps<{ resource: AnyResourceRead }>();
const model = defineModel<components['schemas']['AnnotationsConfig']>({
  required: true,
});
</script>

<template>
  <form-section-heading
    :label="$t('resources.settings.config.annotations.annoDisplayHeading', 2)"
  />

  <!-- ANNOTATION DISPLAY GROUPS -->
  <n-form-item>
    <template #label>
      <n-flex align="center">
        {{ $t('resources.settings.config.annotations.annotationGroup', 2) }}
        <help-button-widget help-key="textAnnotationGroups" />
      </n-flex>
    </template>
    <n-dynamic-input
      v-model:value="model.groups"
      show-sort-button
      :min="0"
      :max="32"
      :create-button-props="dynInputCreateBtnProps"
      @create="() => ({ key: '', translations: [{ locale: '*', translation: '' }] })"
    >
      <template #default="{ index }">
        <n-flex align="flex-start" style="width: 100%">
          <n-form-item
            ignore-path-change
            :label="$t('common.key')"
            :path="`config.special.annotations.groups[${index}].key`"
            :rule="typeSpecificResourceConfigFormRules.textAnnotation.annotationGroupKey"
          >
            <n-input
              v-model:value="model.groups[index].key"
              :placeholder="$t('common.key')"
              @keydown.enter.prevent
            />
          </n-form-item>
          <translation-form-item
            v-model="model.groups[index].translations"
            ignore-path-change
            secondary
            :parent-form-path-prefix="`config.special.annotations.groups[${index}].translations`"
            style="flex: 2"
            :main-form-label="$t('resources.settings.config.annotations.annotationGroup', 1)"
            :translation-form-label="$t('resources.settings.config.annotations.annotationGroup', 1)"
            :translation-form-rules="
              typeSpecificResourceConfigFormRules.textAnnotation.annotationGroupTranslation
            "
          />
        </n-flex>
      </template>
      <template #action="{ index, create, remove, move }">
        <dynamic-input-controls
          top-offset
          :move-up-disabled="index === 0"
          :move-down-disabled="index === model.groups.length - 1"
          :insert-disabled="(model.groups.length || 0) >= 32"
          @move-up="() => move('up', index)"
          @move-down="() => move('down', index)"
          @remove="() => remove(index)"
          @insert="() => create(index)"
        />
      </template>
      <template #create-button-default>
        {{ $t('common.add') }}
      </template>
    </n-dynamic-input>
  </n-form-item>

  <!-- ANNOTATION DISPLAY TEMPLATE -->
  <n-form-item
    :rule="typeSpecificResourceConfigFormRules.textAnnotation.displayTemplate"
    path="config.special.annotations.displayTemplate"
  >
    <template #label>
      <n-flex align="center">
        {{ $t('resources.settings.config.annotations.displayTemplate', 2) }}
        <help-button-widget help-key="textAnnotationDisplayTemplate" />
      </n-flex>
    </template>
    <n-input
      v-model:value="model.displayTemplate"
      type="textarea"
      rows="3"
      style="font-family: monospace"
    />
  </n-form-item>

  <!-- MULTI VALUE DELIMITER -->
  <n-form-item
    :label="$t('resources.settings.config.annotations.multiValueDelimiter')"
    :rule="typeSpecificResourceConfigFormRules.textAnnotation.multiValueDelimiter"
    path="config.special.annotations.multiValueDelimiter"
  >
    <n-input v-model:value="model.multiValueDelimiter" />
  </n-form-item>
</template>
