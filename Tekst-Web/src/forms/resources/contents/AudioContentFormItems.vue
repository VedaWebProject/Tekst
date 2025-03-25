<script setup lang="ts">
import type { AudioContentCreate, AudioResourceRead } from '@/api';
import { dynInputCreateBtnProps } from '@/common';
import NInputOsk from '@/components/NInputOsk.vue';
import { useMessages } from '@/composables/messages';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { contentFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { checkUrl } from '@/utils';
import { cloneDeep } from 'lodash-es';
import { NDynamicInput, NFlex, NFormItem, NInput, useThemeVars } from 'naive-ui';
import { defaultContentModels } from './defaultContentModels';

defineProps<{
  resource: AudioResourceRead;
}>();

const model = defineModel<AudioContentCreate>({ required: true });
const { message } = useMessages();
const tuiTheme = useThemeVars();

async function checkUrlInput(input: HTMLInputElement) {
  const url = input.value;
  if (url && !(await checkUrl(url))) {
    message.warning($t('contents.warnUrlInvalid', { url }), undefined, 3);
    input.style.color = tuiTheme.value.errorColor;
  } else {
    input.style.color = tuiTheme.value.successColor;
  }
}
</script>

<template>
  <!-- FILES -->
  <n-form-item :label="$t('resources.types.audio.contentFields.files')" path="files">
    <n-dynamic-input
      v-model:value="model.files"
      :min="1"
      :max="100"
      :create-button-props="dynInputCreateBtnProps"
      @create="() => cloneDeep(defaultContentModels.audio.files[0])"
    >
      <template #default="{ index }">
        <n-flex align="start" style="flex: 2">
          <!-- URL -->
          <n-form-item
            ignore-path-change
            :label="$t('common.url')"
            :path="`files[${index}].url`"
            :rule="contentFormRules.audio.url"
            style="flex: 2"
          >
            <n-input
              v-model:value="model.files[index].url"
              :placeholder="$t('common.url')"
              @input-blur="checkUrlInput($event.target as HTMLInputElement)"
              @keydown.enter.prevent
            />
          </n-form-item>
          <!-- SOURCE WEBSITE URL -->
          <n-form-item
            ignore-path-change
            :label="$t('resources.types.audio.contentFields.sourceUrl')"
            :path="`files[${index}].sourceUrl`"
            :rule="contentFormRules.common.optionalUrl"
            style="flex: 2"
          >
            <n-input
              v-model:value="model.files[index].sourceUrl"
              :placeholder="$t('resources.types.audio.contentFields.sourceUrl')"
              @keydown.enter.prevent
            />
          </n-form-item>
          <!-- CAPTION -->
          <n-form-item
            ignore-path-change
            :label="$t('common.caption')"
            :path="`files[${index}].caption`"
            :rule="contentFormRules.audio.caption"
            style="flex: 2"
          >
            <n-input-osk
              v-model="model.files[index].caption"
              type="textarea"
              :font="resource.config.general.font || undefined"
              :osk-key="resource.config.common.osk || undefined"
              :rows="2"
              :max-length="512"
              :placeholder="$t('common.caption')"
              :dir="resource.config.common.rtl ? 'rtl' : undefined"
            />
          </n-form-item>
        </n-flex>
      </template>
      <template #action="{ index, create, remove, move }">
        <dynamic-input-controls
          top-offset
          movable
          :insert-disabled="(model.files.length || 0) >= 100"
          :remove-disabled="model.files.length <= 1"
          :move-up-disabled="index === 0"
          :move-down-disabled="index === model.files.length - 1"
          @remove="() => remove(index)"
          @insert="() => create(index)"
          @move-up="move('up', index)"
          @move-down="move('down', index)"
        />
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>
