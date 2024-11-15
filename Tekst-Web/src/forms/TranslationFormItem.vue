<script setup lang="ts">
import type { LocaleKey, Translation } from '@/api';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { translationFormRules } from '@/forms/formRules';
import { $t, renderLanguageOptionLabel } from '@/i18n';
import { useStateStore } from '@/stores';
import { NDynamicInput, NFlex, NFormItem, NInput, NSelect, type FormItemRule } from 'naive-ui';
import { computed } from 'vue';

withDefaults(
  defineProps<{
    parentFormPathPrefix: string;
    mainFormLabel?: string;
    translationFormLabel?: string;
    translationFormRule?: FormItemRule[];
    multiline?: boolean;
    maxTranslationLength?: number;
    minItems?: number;
    secondary?: boolean;
    ignorePathChange?: boolean;
  }>(),
  {
    mainFormLabel: undefined,
    translationFormLabel: undefined,
    translationFormRule: undefined,
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
      item-class="mb-0"
      :default-value="[]"
      @create="
        () => ({
          locale: localeOptions.find((o) => !model?.find((t) => t.locale === o.value))?.value,
          translation: '',
        })
      "
    >
      <template #default="{ value: translationValue, index: translationIndex }">
        <n-flex align="flex-start" wrap style="flex-grow: 2">
          <!-- LOCALE -->
          <n-form-item
            v-if="model"
            ignore-path-change
            :show-label="false"
            :show-feedback="false"
            :path="`${parentFormPathPrefix}[${translationIndex}].locale`"
            :rule="translationFormRules.locale"
            style="flex-grow: 1; flex-basis: 200px"
          >
            <n-select
              v-model:value="translationValue.locale"
              :options="localeOptions"
              :placeholder="$t('general.language')"
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
            :rule="translationFormRule"
            style="flex-grow: 2"
          >
            <n-input
              v-model:value="translationValue.translation"
              :type="multiline ? 'textarea' : 'text'"
              :show-count="multiline && !!maxTranslationLength"
              :maxlength="maxTranslationLength"
              :placeholder="translationFormLabel"
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
    </n-dynamic-input>
  </n-form-item>
</template>
