<script setup lang="ts">
import type { ExternalReferencesContentCreate, ExternalReferencesResourceRead } from '@/api';
import { dynInputCreateBtnProps } from '@/common';
import OskInput from '@/components/OskInput.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { contentFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { cloneDeep } from 'lodash-es';
import { NDynamicInput, NFlex, NFormItem, NInput } from 'naive-ui';
import { defaultContentModels } from './defaultContentModels';

defineProps<{
  resource: ExternalReferencesResourceRead;
}>();

const model = defineModel<ExternalReferencesContentCreate>({ required: true });
</script>

<template>
  <!-- LINKS -->
  <n-form-item :show-label="false" path="links">
    <n-dynamic-input
      v-model:value="model.links"
      :min="1"
      :max="100"
      :create-button-props="dynInputCreateBtnProps"
      @create="() => cloneDeep(defaultContentModels.externalReferences.links[0])"
    >
      <template #default="{ index }">
        <n-flex align="start" style="flex: 2">
          <!-- URL -->
          <n-form-item
            ignore-path-change
            :label="$t('common.url')"
            :path="`links[${index}].url`"
            :rule="contentFormRules.externalReferences.url"
            style="flex: 2"
          >
            <n-input
              v-model:value="model.links[index].url"
              :placeholder="$t('common.url')"
              @keydown.enter.prevent
            />
          </n-form-item>
          <!-- TITLE -->
          <n-form-item
            ignore-path-change
            :label="$t('resources.types.externalReferences.contentFields.title')"
            :path="`links[${index}].title`"
            :rule="contentFormRules.externalReferences.title"
            style="flex: 2"
          >
            <osk-input
              v-model="model.links[index].title"
              :font="resource.config.general.font || undefined"
              :osk-key="resource.config.general.osk || undefined"
              :max-length="128"
              :placeholder="$t('resources.types.externalReferences.contentFields.title')"
              :dir="resource.config.general.rtl ? 'rtl' : undefined"
            />
          </n-form-item>
          <!-- DESCRIPTION -->
          <n-form-item
            ignore-path-change
            :label="$t('common.description')"
            :path="`links[${index}].description`"
            :rule="contentFormRules.externalReferences.description"
            style="flex: 2"
          >
            <osk-input
              v-model="model.links[index].description"
              type="textarea"
              :font="resource.config.general.font || undefined"
              :osk-key="resource.config.general.osk || undefined"
              :rows="2"
              :max-length="4096"
              :placeholder="$t('common.description')"
              :dir="resource.config.general.rtl ? 'rtl' : undefined"
            />
          </n-form-item>
        </n-flex>
      </template>
      <template #action="{ index, create, remove, move }">
        <dynamic-input-controls
          top-offset
          movable
          :insert-disabled="(model.links.length || 0) >= 100"
          :remove-disabled="model.links.length <= 1"
          :move-up-disabled="index === 0"
          :move-down-disabled="index === model.links.length - 1"
          @remove="() => remove(index)"
          @insert="() => create(index)"
          @move-up="move('up', index)"
          @move-down="move('down', index)"
        />
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>
