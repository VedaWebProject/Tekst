<script setup lang="ts">
import type { AudioContentCreate, AudioResourceRead } from '@/api';
import { NFlex, NFormItem, NInput, NDynamicInput } from 'naive-ui';
import { contentFormRules } from '@/forms/formRules';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import NInputOsk from '@/components/NInputOsk.vue';
import { checkUrl } from '@/utils';
import { $t } from '@/i18n';
import { useMessages } from '@/composables/messages';

defineProps<{
  resource: AudioResourceRead;
}>();

const model = defineModel<AudioContentCreate>({ required: true });
const { message } = useMessages();

function handleUpdate(field: string, value: any) {
  model.value = {
    ...model.value,
    [field]: value,
  };
}

async function checkUrlInput(input: HTMLInputElement) {
  const url = input.value;
  if (url && !(await checkUrl(url))) {
    message.warning($t('contents.warnUrlInvalid', { url }), undefined, 3);
    input.classList.add('invalid-url');
  } else {
    input.classList.remove('invalid-url');
  }
}
</script>

<template>
  <!-- FILES -->
  <n-form-item :label="$t('resources.types.audio.contentFields.files')" path="files">
    <n-dynamic-input
      :value="model.files"
      :min="1"
      :max="100"
      @create="() => ({ url: undefined, caption: undefined })"
      @update:value="(value) => handleUpdate('files', value)"
    >
      <template #default="{ index }">
        <n-flex align="start" style="flex-grow: 2">
          <!-- URL -->
          <n-form-item
            ignore-path-change
            :label="$t('resources.types.audio.contentFields.url')"
            :path="`files[${index}].url`"
            :rule="contentFormRules.audio.url"
            style="flex-grow: 2"
          >
            <n-input
              v-model:value="model.files[index].url"
              :placeholder="$t('resources.types.audio.contentFields.url')"
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
            style="flex-grow: 2"
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
            :label="$t('resources.types.audio.contentFields.caption')"
            :path="`files[${index}].caption`"
            :rule="contentFormRules.audio.caption"
            style="flex-grow: 2"
          >
            <n-input-osk
              v-model="model.files[index].caption"
              type="textarea"
              :font="resource.config.general.font || undefined"
              :rows="2"
              :max-length="512"
              :placeholder="$t('resources.types.audio.contentFields.caption')"
            />
          </n-form-item>
        </n-flex>
      </template>
      <template #action="{ index: indexAction, create, remove, move }">
        <dynamic-input-controls
          top-offset
          movable
          :insert-disabled="(model.files.length || 0) >= 100"
          :remove-disabled="model.files.length <= 1"
          :move-up-disabled="indexAction === 0"
          :move-down-disabled="indexAction === model.files.length - 1"
          @remove="() => remove(indexAction)"
          @insert="() => create(indexAction)"
          @move-up="move('up', indexAction)"
          @move-down="move('down', indexAction)"
        />
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>
