<script setup lang="ts">
import type { ApiCallContentCreate, ApiCallResourceRead } from '@/api';
import { useMessages } from '@/composables/messages';
import { contentFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { checkUrl } from '@/utils';
import { NFormItem, NInput, useThemeVars } from 'naive-ui';

defineProps<{
  resource: ApiCallResourceRead;
}>();

const model = defineModel<ApiCallContentCreate>({ required: true });
const { message } = useMessages();
const tuiTheme = useThemeVars();

async function checkUrlInput(input: HTMLInputElement) {
  const url = input.value;
  if (url && !(await checkUrl(url, 'GET'))) {
    message.warning($t('contents.warnUrlInvalid', { url }), undefined, 3);
    if (input.style) {
      input.style.color = tuiTheme.value.errorColor;
    }
  } else {
    if (input.style) {
      input.style.color = tuiTheme.value.successColor;
    }
  }
}
</script>

<template>
  <n-form-item
    :label="$t('resources.types.apiCall.contentFields.url')"
    path="url"
    :rule="contentFormRules.apiCall.url"
  >
    <n-input
      v-model:value="model.url"
      :placeholder="$t('resources.types.apiCall.contentFields.url')"
      @input-blur="checkUrlInput($event.target as HTMLInputElement)"
      @keydown.enter.prevent
    />
  </n-form-item>
</template>
