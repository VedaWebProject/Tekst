<script setup lang="ts">
import type { components } from '@/api/schema';
import IconHeading from '@/components/generic/IconHeading.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { searchReplacementsConfigFormRules } from '@/forms/formRules';
import { NDynamicInput, NFlex, NFormItem, NInput } from 'naive-ui';

const model = defineModel<components['schemas']['SearchReplacements']>({ required: true });
</script>

<template>
  <icon-heading level="5">
    <span>{{ $t('resources.settings.config.general.searchReplacements.heading') }}</span>
    <help-button-widget help-key="searchReplacements" />
  </icon-heading>
  <n-form-item :show-label="false">
    <n-dynamic-input
      v-model:value="model"
      :min="0"
      :max="16"
      :show-sort-button="false"
      @create="() => ({ pattern: '', replacement: '' })"
    >
      <template #default="{ value, index }">
        <n-flex align="flex-start" wrap style="flex-grow: 2">
          <!-- PATTERN -->
          <n-form-item
            ignore-path-change
            :label="$t('resources.settings.config.general.searchReplacements.pattern')"
            :path="`config.general.searchReplacements[${index}].pattern`"
            :rule="searchReplacementsConfigFormRules.pattern"
            style="flex-grow: 1; flex-basis: 200px"
          >
            <n-input
              v-model:value="value.pattern"
              :placeholder="$t('resources.settings.config.general.searchReplacements.pattern')"
              @keydown.enter.prevent
            />
          </n-form-item>
          <!-- REPLACEMENT -->
          <n-form-item
            ignore-path-change
            :label="$t('resources.settings.config.general.searchReplacements.replacement')"
            :path="`config.general.searchReplacements[${index}].replacement`"
            :rule="searchReplacementsConfigFormRules.replacement"
            style="flex-grow: 1; flex-basis: 200px"
          >
            <n-input
              v-model:value="value.replacement"
              :placeholder="$t('resources.settings.config.general.searchReplacements.replacement')"
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
    </n-dynamic-input>
  </n-form-item>
</template>
