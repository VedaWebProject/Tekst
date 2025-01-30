<script setup lang="ts">
import type { components } from '@/api/schema';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { typeSpecificResourceConfigFormRules } from '@/forms/formRules';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import { NDynamicInput, NFlex, NFormItem, NInput } from 'naive-ui';

const model = defineModel<
  components['schemas']['TextAnnotationResourceConfig']['annotationGroups']
>({
  required: true,
});
</script>

<template>
  <!-- ANNOTATION DISPLAY GROUPS -->
  <n-form-item v-if="model">
    <template #label>
      <n-flex align="center">
        {{ $t('resources.settings.config.annotationGroup', 2) }}
        <help-button-widget help-key="textAnnotationGroups" />
      </n-flex>
    </template>
    <n-dynamic-input
      v-model:value="model"
      show-sort-button
      :min="0"
      :max="32"
      @create="() => ({ key: '', translations: [{ locale: '*', translation: '' }] })"
    >
      <template #default="{ index }">
        <n-flex align="flex-start" style="width: 100%">
          <n-form-item
            ignore-path-change
            :label="$t('general.key')"
            :path="`config.annotationGroups[${index}].key`"
            :rule="typeSpecificResourceConfigFormRules.textAnnotation.annotationGroupKey"
          >
            <n-input
              v-model:value="model[index].key"
              :placeholder="$t('general.key')"
              @keydown.enter.prevent
            />
          </n-form-item>
          <translation-form-item
            v-model="model[index].translations"
            ignore-path-change
            secondary
            :parent-form-path-prefix="`config.annotationGroups[${index}].translations`"
            style="flex-grow: 2"
            :main-form-label="$t('resources.settings.config.annotationGroup', 1)"
            :translation-form-label="$t('resources.settings.config.annotationGroup', 1)"
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
          :move-down-disabled="indexAction === model.length - 1"
          :insert-disabled="(model.length || 0) >= 32"
          @move-up="() => move('up', indexAction)"
          @move-down="() => move('down', indexAction)"
          @remove="() => remove(indexAction)"
          @insert="() => create(indexAction)"
        />
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>
