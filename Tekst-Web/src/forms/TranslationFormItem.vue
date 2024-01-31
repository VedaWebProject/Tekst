<script setup lang="ts">
import type { Translation, LocaleKey } from '@/api';
import { $t, renderLanguageOptionLabel } from '@/i18n';
import {
  NButton,
  NSpace,
  NIcon,
  NFormItem,
  NSelect,
  NDynamicInput,
  NInput,
  type FormItemRule,
} from 'naive-ui';
import { computed } from 'vue';
import { translationFormRules } from '@/forms/formRules';
import { useStateStore } from '@/stores';

import { AddIcon, MinusIcon } from '@/icons';

const props = withDefaults(
  defineProps<{
    value: Translation[] | undefined;
    parentFormPathPrefix: string;
    mainFormLabel?: string;
    translationFormLabel?: string;
    translationFormRule?: FormItemRule[];
    multiline?: boolean;
    maxTranslationLength?: number;
    minItems?: number;
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

const emit = defineEmits(['update:value']);

const state = useStateStore();

const localeOptions = computed(() =>
  state.translationLocaleOptions.map((tlo) => ({
    ...tlo,
    disabled: !!props.value
      ?.map((lvlTrans: Translation) => lvlTrans.locale)
      .includes(tlo.value as LocaleKey),
  }))
);
</script>

<template>
  <n-form-item
    :show-label="!!mainFormLabel"
    :label="mainFormLabel"
    :show-feedback="!value || !value.length"
  >
    <n-dynamic-input
      :value="value"
      :min="minItems"
      :max="localeOptions.length"
      item-style="margin-bottom: 0;"
      :default-value="[]"
      @create="
        () => ({
          locale: localeOptions.find((o) => !value?.find((t) => t.locale === o.value))?.value,
          translation: '',
        })
      "
      @update:value="(value) => emit('update:value', value)"
    >
      <template #default="{ value: translationValue, index: translationIndex }">
        <div style="display: flex; align-items: flex-start; gap: 12px; width: 100%">
          <!-- LOCALE -->
          <n-form-item
            v-if="value"
            ignore-path-change
            :show-label="false"
            :path="`${parentFormPathPrefix}[${translationIndex}].locale`"
            :rule="translationFormRules.locale"
          >
            <n-select
              v-model:value="translationValue.locale"
              :options="localeOptions"
              :placeholder="$t('general.language')"
              :consistent-menu-width="false"
              :render-label="(o) => renderLanguageOptionLabel(localeOptions, o)"
              style="min-width: 200px; font-weight: var(--app-ui-font-weight-normal)"
              @keydown.enter.prevent
            />
          </n-form-item>
          <!-- TRANSLATION -->
          <n-form-item
            v-if="value"
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
        </div>
      </template>
      <template #action="{ index: actionIndex, create, remove }">
        <n-space style="margin-left: 20px; flex-wrap: nowrap">
          <n-button
            secondary
            circle
            :title="$t('translationFormItem.tipBtnRemove')"
            :disabled="!value || value.length === minItems"
            @click="() => remove(actionIndex)"
          >
            <template #icon>
              <n-icon :component="MinusIcon" />
            </template>
          </n-button>
          <n-button
            secondary
            circle
            :title="$t('translationFormItem.tipBtnAdd')"
            :disabled="value && value.length >= localeOptions.length"
            @click="() => create(actionIndex)"
          >
            <template #icon>
              <n-icon :component="AddIcon" />
            </template>
          </n-button>
        </n-space>
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>
