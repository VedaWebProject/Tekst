<script setup lang="ts">
import type { ImagesContentCreate, ImagesResourceRead } from '@/api';
import { NFlex, NFormItem, NInput, NDynamicInput } from 'naive-ui';
import { contentFormRules } from '@/forms/formRules';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import NInputOsk from '@/components/NInputOsk.vue';

defineProps<{
  resource: ImagesResourceRead;
}>();

const model = defineModel<ImagesContentCreate>({ required: true });

function handleUpdate(field: string, value: any) {
  model.value = {
    ...model.value,
    [field]: value,
  };
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
        <n-flex align="start" style="flex-grow: 2">
          <!-- URL -->
          <n-form-item
            ignore-path-change
            :label="$t('resources.types.images.contentFields.url')"
            :path="`files[${index}].url`"
            :rule="contentFormRules.images.url"
            style="flex-grow: 2"
          >
            <n-input
              v-model:value="model.files[index].url"
              :placeholder="$t('resources.types.images.contentFields.url')"
              @keydown.enter.prevent
            />
          </n-form-item>
          <!-- CAPTION -->
          <n-form-item
            ignore-path-change
            :label="$t('resources.types.images.contentFields.caption')"
            :path="`files[${index}].caption`"
            :rule="contentFormRules.images.caption"
            style="flex-grow: 2"
          >
            <n-input-osk
              v-model="model.files[index].caption"
              type="textarea"
              :font="resource.config?.general?.font || undefined"
              :rows="2"
              :max-length="512"
              :placeholder="$t('resources.types.images.contentFields.caption')"
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
