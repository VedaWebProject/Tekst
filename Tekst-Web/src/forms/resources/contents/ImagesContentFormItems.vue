<script setup lang="ts">
import type { ImagesContentCreate, ImagesResourceRead } from '@/api';
import NInputOsk from '@/components/NInputOsk.vue';
import { useMessages } from '@/composables/messages';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { contentFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { checkUrl } from '@/utils';
import { NDynamicInput, NFlex, NFormItem, NInput, useThemeVars } from 'naive-ui';

defineProps<{
  resource: ImagesResourceRead;
}>();

const model = defineModel<ImagesContentCreate>({ required: true });
const { message } = useMessages();
const tuiTheme = useThemeVars();

function handleUpdate(field: string, value: unknown) {
  model.value = {
    ...model.value,
    [field]: value,
  };
}

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
  <n-form-item :label="$t('resources.types.images.contentFields.files')" path="files">
    <n-dynamic-input
      :value="model.files"
      :min="1"
      :max="100"
      @create="() => ({ url: undefined, caption: undefined })"
      @update:value="(value) => handleUpdate('files', value)"
    >
      <template #default="{ index }">
        <n-flex align="stretch" style="flex-grow: 2">
          <n-flex vertical style="flex-grow: 2">
            <!-- URL -->
            <n-form-item
              ignore-path-change
              :label="$t('resources.types.images.contentFields.url')"
              :path="`files[${index}].url`"
              :rule="contentFormRules.images.url"
            >
              <n-input
                v-model:value="model.files[index].url"
                :placeholder="$t('resources.types.images.contentFields.url')"
                @input-blur="checkUrlInput($event.target as HTMLInputElement)"
                @keydown.enter.prevent
              />
            </n-form-item>
            <!-- THUMBNAIL URL -->
            <n-form-item
              ignore-path-change
              :label="$t('resources.types.images.contentFields.thumbUrl')"
              :path="`files[${index}].thumbUrl`"
              :rule="contentFormRules.common.optionalUrl"
            >
              <n-input
                v-model:value="model.files[index].thumbUrl"
                :placeholder="$t('resources.types.images.contentFields.thumbUrl')"
                @input-blur="checkUrlInput($event.target as HTMLInputElement)"
                @keydown.enter.prevent
              />
            </n-form-item>
            <!-- Source URL -->
            <n-form-item
              ignore-path-change
              :label="$t('resources.types.images.contentFields.sourceUrl')"
              :path="`files[${index}].sourceUrl`"
              :rule="contentFormRules.common.optionalUrl"
            >
              <n-input
                v-model:value="model.files[index].sourceUrl"
                :placeholder="$t('resources.types.images.contentFields.sourceUrl')"
                @keydown.enter.prevent
              />
            </n-form-item>
          </n-flex>
          <!-- CAPTION -->
          <n-form-item
            ignore-path-change
            :label="$t('general.caption')"
            :path="`files[${index}].caption`"
            :rule="contentFormRules.images.caption"
            style="flex-grow: 2"
          >
            <n-input-osk
              v-model="model.files[index].caption"
              type="textarea"
              class="caption-textarea"
              :font="resource.config.general.font || undefined"
              :osk-key="resource.config.common.osk || undefined"
              style="height: 100%"
              :max-length="512"
              :placeholder="$t('general.caption')"
              :dir="resource.config.common.rtl ? 'rtl' : undefined"
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

<style scoped>
:deep(.caption-textarea.n-input.n-input--textarea.n-input--resizable .n-input-wrapper) {
  resize: none;
}
</style>
