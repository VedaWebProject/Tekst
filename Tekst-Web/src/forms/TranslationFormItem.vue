<script setup lang="ts">
import type { LocaleKey, Translation } from '@/api';
import { dynInputCreateBtnProps } from '@/common';
import HtmlEditor from '@/components/editors/HtmlEditor.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { commonFormRules } from '@/forms/formRules';
import { $t, renderLanguageOptionLabel } from '@/i18n';
import { useStateStore } from '@/stores';
import { NDynamicInput, NFlex, NFormItem, NInput, NSelect, type FormItemRule } from 'naive-ui';
import { computed } from 'vue';

withDefaults(
  defineProps<{
    parentFormPathPrefix: string;
    mainFormLabel?: string;
    translationFormLabel?: string;
    translationFormRules?: FormItemRule[];
    inputType?: 'input' | 'textarea' | 'html';
    maxTranslationLength?: number;
    minItems?: number;
    secondary?: boolean;
    ignorePathChange?: boolean;
  }>(),
  {
    mainFormLabel: undefined,
    translationFormLabel: undefined,
    translationFormRule: undefined,
    inputType: 'input',
    multiline: false,
    maxTranslationLength: undefined,
    minItems: 0,
  }
);

const model = defineModel<Translation[]>();

const state = useStateStore();

const localeOptions = computed(() =>
  state.translationLocaleOptions.map((tlo) => ({
    ...tlo,
    disabled: model.value?.map((t: Translation) => t.locale).includes(tlo.value as LocaleKey),
  }))
);
</script>

<template>
  <n-form-item
    :show-label="!!mainFormLabel"
    :label="mainFormLabel"
    :show-feedback="!model || !model.length"
    :path="parentFormPathPrefix"
    :ignore-path-change="ignorePathChange"
  >
    <n-dynamic-input
      v-model:value="model"
      :min="minItems"
      :max="localeOptions.length"
      :item-class="state.smallScreen ? undefined : 'mb-0'"
      :default-value="[]"
      :create-button-props="dynInputCreateBtnProps"
      @create="
        () => ({
          locale: localeOptions.find((o) => !model?.find((t) => t.locale === o.value))?.value,
          translation: '',
        })
      "
    >
      <template #default="{ value: translationValue, index: translationIndex }">
        <n-flex
          :vertical="inputType === 'html'"
          align="flex-start"
          :wrap="inputType !== 'html'"
          style="flex: 2"
        >
          <!-- LOCALE -->
          <n-form-item
            v-if="model"
            ignore-path-change
            :show-label="false"
            :show-feedback="false"
            :path="`${parentFormPathPrefix}[${translationIndex}].locale`"
            :rule="commonFormRules.locale"
            :style="{
              flex: inputType !== 'html' ? '1 200px' : undefined,
              width: inputType !== 'html' ? undefined : '100%',
            }"
          >
            <n-select
              v-model:value="translationValue.locale"
              :options="localeOptions"
              :placeholder="$t('common.language')"
              :consistent-menu-width="false"
              :render-label="(o) => renderLanguageOptionLabel(localeOptions, o)"
              @keydown.enter.prevent
            />
          </n-form-item>
          <!-- TRANSLATION -->
          <n-form-item
            v-if="model"
            ignore-path-change
            :show-label="false"
            :path="`${parentFormPathPrefix}[${translationIndex}].translation`"
            :rule="translationFormRules"
            :style="{
              flex: inputType !== 'html' ? '1 200px' : undefined,
              width: inputType !== 'html' ? undefined : '100%',
            }"
          >
            <n-input
              v-if="inputType === 'input' || inputType === 'textarea'"
              v-model:value="translationValue.translation"
              :type="inputType === 'textarea' ? 'textarea' : 'text'"
              :show-count="inputType === 'textarea' && !!maxTranslationLength"
              :maxlength="maxTranslationLength"
              :placeholder="translationFormLabel"
            />
            <html-editor
              v-else-if="inputType === 'html'"
              v-model:value="translationValue.translation"
              :max-chars="maxTranslationLength"
            />
          </n-form-item>
        </n-flex>
      </template>
      <template #action="{ index: actionIndex, create, remove }">
        <dynamic-input-controls
          :secondary="secondary"
          :movable="false"
          :remove-title="$t('translationFormItem.tipBtnRemove')"
          :remove-disabled="!model || model.length === minItems"
          :insert-title="$t('translationFormItem.tipBtnAdd')"
          :insert-disabled="model && model.length >= localeOptions.length"
          @remove="() => remove(actionIndex)"
          @insert="() => create(actionIndex)"
        />
      </template>
      <template #create-button-default>
        {{ $t('common.add') }}
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>
