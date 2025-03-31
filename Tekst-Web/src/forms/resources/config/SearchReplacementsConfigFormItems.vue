<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import type { components } from '@/api/schema';
import { dynInputCreateBtnProps } from '@/common';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { searchReplacementsConfigFormRules } from '@/forms/formRules';
import { NDynamicInput, NFlex, NFormItem, NInput } from 'naive-ui';

defineProps<{ resource: AnyResourceRead }>();
const model = defineModel<components['schemas']['SearchReplacements']>({ required: true });
</script>

<template>
  <form-section-heading
    :label="$t('resources.settings.config.searchReplacements.heading')"
    help-key="searchReplacements"
  />
  <n-form-item :show-label="false">
    <n-dynamic-input
      v-model:value="model"
      :min="0"
      :max="16"
      :show-sort-button="false"
      :create-button-props="dynInputCreateBtnProps"
      @create="() => ({ pattern: '', replacement: '' })"
    >
      <template #default="{ value, index }">
        <n-flex align="flex-start" wrap style="flex: 2">
          <!-- PATTERN -->
          <n-form-item
            ignore-path-change
            :label="$t('resources.settings.config.searchReplacements.pattern')"
            :path="`config.special.searchReplacements[${index}].pattern`"
            :rule="searchReplacementsConfigFormRules.pattern"
            style="flex: 1 200px"
          >
            <n-input
              v-model:value="value.pattern"
              :placeholder="$t('resources.settings.config.searchReplacements.pattern')"
              @keydown.enter.prevent
            />
          </n-form-item>
          <!-- REPLACEMENT -->
          <n-form-item
            ignore-path-change
            :label="$t('resources.settings.config.searchReplacements.replacement')"
            :path="`config.special.searchReplacements[${index}].replacement`"
            :rule="searchReplacementsConfigFormRules.replacement"
            style="flex: 1 200px"
          >
            <n-input
              v-model:value="value.replacement"
              :placeholder="$t('resources.settings.config.searchReplacements.replacement')"
              @keydown.enter.prevent
            />
          </n-form-item>
        </n-flex>
      </template>
      <template #action="{ index, create, remove }">
        <dynamic-input-controls
          top-offset
          :movable="false"
          :insert-disabled="(model.length || 0) >= 16"
          @remove="() => remove(index)"
          @insert="() => create(index)"
        />
      </template>
      <template #create-button-default>
        {{ $t('common.add') }}
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>
