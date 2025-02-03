<script setup lang="ts">
import type { components } from '@/api/schema';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { typeSpecificResourceConfigFormRules } from '@/forms/formRules';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import { NDynamicInput, NFlex, NFormItem, NInput } from 'naive-ui';

const model = defineModel<components['schemas']['TextAnnotationSpecialConfig']>({
  required: true,
});

function handleUpdate(field: string, value: unknown) {
  model.value = {
    ...model.value,
    [field]: value,
  };
}
</script>

<template>
  <!-- ANNOTATION DISPLAY GROUPS -->
  <n-form-item>
    <template #label>
      <n-flex align="center">
        {{ $t('resources.settings.config.textAnnotation.annotationGroup', 2) }}
        <help-button-widget help-key="textAnnotationGroups" />
      </n-flex>
    </template>
    <n-dynamic-input
      :value="model.annotationGroups"
      show-sort-button
      :min="0"
      :max="32"
      @create="() => ({ key: '', translations: [{ locale: '*', translation: '' }] })"
      @update:value="(v) => handleUpdate('annotationGroups', v)"
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
            style="flex-grow: 2"
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
      <template #action="{ index: indexAction, create, remove, move }">
        <dynamic-input-controls
          top-offset
          :move-up-disabled="indexAction === 0"
          :move-down-disabled="indexAction === model.annotationGroups.length - 1"
          :insert-disabled="(model.annotationGroups.length || 0) >= 32"
          @move-up="() => move('up', indexAction)"
          @move-down="() => move('down', indexAction)"
          @remove="() => remove(indexAction)"
          @insert="() => create(indexAction)"
        />
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
      :value="model.displayTemplate"
      type="textarea"
      rows="3"
      style="font-family: monospace"
      @update:value="(v) => handleUpdate('displayTemplate', v)"
    />
  </n-form-item>

  <!-- MULTI VALUE DELIMITER -->
  <n-form-item
    :label="$t('resources.settings.config.textAnnotation.multiValueDelimiter')"
    :rule="typeSpecificResourceConfigFormRules.textAnnotation.multiValueDelimiter"
    path="config.textAnnotation.multiValueDelimiter"
  >
    <n-input
      :value="model.multiValueDelimiter"
      @update:value="(v) => handleUpdate('multiValueDelimiter', v)"
    />
  </n-form-item>
</template>
