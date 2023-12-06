<script setup lang="ts">
import type { Translation, Locale } from '@/api';
import { $t, localeProfiles } from '@/i18n';
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
import { translationFormRules } from '@/formRules';

import AddRound from '@vicons/material/AddRound';
import MinusRound from '@vicons/material/MinusRound';

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
    loading?: boolean;
    disabled?: boolean;
  }>(),
  {
    mainFormLabel: undefined,
    translationFormLabel: undefined,
    translationFormRule: undefined,
    multiline: false,
    maxTranslationLength: undefined,
    minItems: 0,
    loading: false,
    disabled: false,
  }
);

const emits = defineEmits(['update:value']);

const localeOptions = computed(() =>
  [
    {
      label: `🌐 ${$t('models.locale.allLanguages')}`,
      value: '*',
      disabled: !!props.value?.map((lvlTrans: Translation) => lvlTrans.locale).includes('*'),
    },
  ].concat(
    Object.keys(localeProfiles).map((l: string) => ({
      label: `${localeProfiles[l].icon} ${localeProfiles[l].displayFull}`,
      value: localeProfiles[l].key,
      disabled: !!props.value
        ?.map((lvlTrans: Translation) => lvlTrans.locale)
        .includes(l as Locale),
    }))
  )
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
      :disabled="loading || disabled"
      :default-value="[]"
      @create="
        () => ({
          locale: localeOptions.find((o) => !value?.find((t) => t.locale === o.value))?.value,
          translation: '',
        })
      "
      @update:value="(value) => emits('update:value', value)"
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
              :disabled="loading"
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
              :disabled="loading"
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
              <n-icon :component="MinusRound" />
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
              <n-icon :component="AddRound" />
            </template>
          </n-button>
        </n-space>
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>
