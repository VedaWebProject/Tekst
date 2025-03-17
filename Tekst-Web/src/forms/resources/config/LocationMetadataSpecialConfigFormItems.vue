<script setup lang="ts">
import type { components } from '@/api/schema';
import { dynInputCreateBtnProps } from '@/common';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { typeSpecificResourceConfigFormRules } from '@/forms/formRules';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import { NDynamicInput, NFlex, NFormItem, NInput } from 'naive-ui';

const model = defineModel<components['schemas']['LocationMetadataSpecialConfig']>({
  required: true,
});
</script>

<template>
  <form-section-heading :label="$t('resources.settings.config.locationMetadata.metaGroupsHeading')" />

  <!-- ANNOTATION DISPLAY GROUPS -->
  <n-form-item>
    <template #label>
      <n-flex align="center">
        {{ $t('resources.settings.config.textAnnotation.annotationGroup', 2) }}
        <help-button-widget help-key="textAnnotationGroups" />
      </n-flex>
    </template>
    <n-dynamic-input
      v-model:value="model.annotationGroups"
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
            :label="$t('general.key')"
            :path="`config.textAnnotation.annotationGroups[${index}].key`"
            :rule="typeSpecificResourceConfigFormRules.textAnnotation.annotationGroupKey"
          >
            <n-input
              v-model:value="model.annotationGroups[index].key"
              :placeholder="$t('general.key')"
              @keydown.enter.prevent
            />
          </n-form-item>
          <translation-form-item
            v-model="model.annotationGroups[index].translations"
            ignore-path-change
            secondary
            :parent-form-path-prefix="`config.textAnnotation.annotationGroups[${index}].translations`"
            style="flex: 2"
            :main-form-label="$t('resources.settings.config.textAnnotation.annotationGroup', 1)"
            :translation-form-label="
              $t('resources.settings.config.textAnnotation.annotationGroup', 1)
            "
            :translation-form-rule="
              typeSpecificResourceConfigFormRules.textAnnotation.annotationGroupTranslation
            "
          />
        </n-flex>
      </template>
      <template #action="{ index, create, remove, move }">
        <dynamic-input-controls
          top-offset
          :move-up-disabled="index === 0"
          :move-down-disabled="index === model.annotationGroups.length - 1"
          :insert-disabled="(model.annotationGroups.length || 0) >= 32"
          @move-up="() => move('up', index)"
          @move-down="() => move('down', index)"
          @remove="() => remove(index)"
          @insert="() => create(index)"
        />
      </template>
      <template #create-button-default>
        {{ $t('general.addAction') }}
      </template>
    </n-dynamic-input>
  </n-form-item>

  <!-- ANNOTATION DISPLAY TEMPLATE -->
  <n-form-item
    :rule="typeSpecificResourceConfigFormRules.textAnnotation.displayTemplate"
    path="config.textAnnotation.displayTemplate"
  >
    <template #label>
      <n-flex align="center">
        {{ $t('resources.settings.config.textAnnotation.displayTemplate', 2) }}
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
    :label="$t('resources.settings.config.textAnnotation.multiValueDelimiter')"
    :rule="typeSpecificResourceConfigFormRules.textAnnotation.multiValueDelimiter"
    path="config.textAnnotation.multiValueDelimiter"
  >
    <n-input v-model:value="model.multiValueDelimiter" />
  </n-form-item>
</template>
