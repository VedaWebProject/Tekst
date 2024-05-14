<script setup lang="ts">
import type { ExternalReferencesContentCreate, ExternalReferencesResourceRead } from '@/api';
import { NFlex, NFormItem, NInput, NDynamicInput } from 'naive-ui';
import { contentFormRules } from '@/forms/formRules';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import NInputOsk from '@/components/NInputOsk.vue';
import { $t } from '@/i18n';

defineProps<{
  resource: ExternalReferencesResourceRead;
}>();

const model = defineModel<ExternalReferencesContentCreate>({ required: true });

function handleUpdate(field: string, value: any) {
  model.value = {
    ...model.value,
    [field]: value,
  };
}
</script>

<template>
  <!-- FILES -->
  <n-form-item :label="$t('resources.types.externalReferences.contentFields.links')" path="links">
    <n-dynamic-input
      :value="model.links"
      :min="1"
      :max="100"
      @create="() => ({ url: undefined, title: undefined, description: undefined })"
      @update:value="(value) => handleUpdate('links', value)"
    >
      <template #default="{ index }">
        <n-flex align="start" style="flex-grow: 2">
          <!-- URL -->
          <n-form-item
            ignore-path-change
            :label="$t('resources.types.externalReferences.contentFields.url')"
            :path="`links[${index}].url`"
            :rule="contentFormRules.externalReferences.url"
            style="flex-grow: 2"
          >
            <n-input
              v-model:value="model.links[index].url"
              :placeholder="$t('resources.types.externalReferences.contentFields.url')"
              @keydown.enter.prevent
            />
          </n-form-item>
          <!-- TITLE -->
          <n-form-item
            ignore-path-change
            :label="$t('resources.types.externalReferences.contentFields.title')"
            :path="`links[${index}].title`"
            :rule="contentFormRules.externalReferences.title"
            style="flex-grow: 2"
          >
            <n-input-osk
              v-model="model.links[index].title"
              :font="resource.config?.general?.font || undefined"
              :max-length="128"
              :placeholder="$t('resources.types.externalReferences.contentFields.title')"
            />
          </n-form-item>
          <!-- DESCRIPTION -->
          <n-form-item
            ignore-path-change
            :label="$t('resources.types.externalReferences.contentFields.description')"
            :path="`links[${index}].description`"
            :rule="contentFormRules.externalReferences.description"
            style="flex-grow: 2"
          >
            <n-input-osk
              v-model="model.links[index].description"
              type="textarea"
              :font="resource.config?.general?.font || undefined"
              :rows="2"
              :max-length="4096"
              :placeholder="$t('resources.types.externalReferences.contentFields.description')"
            />
          </n-form-item>
        </n-flex>
      </template>
      <template #action="{ index: indexAction, create, remove, move }">
        <dynamic-input-controls
          top-offset
          movable
          :insert-disabled="(model.links.length || 0) >= 100"
          :remove-disabled="model.links.length <= 1"
          :move-up-disabled="indexAction === 0"
          :move-down-disabled="indexAction === model.links.length - 1"
          @remove="() => remove(indexAction)"
          @insert="() => create(indexAction)"
          @move-up="move('up', indexAction)"
          @move-down="move('down', indexAction)"
        />
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>
