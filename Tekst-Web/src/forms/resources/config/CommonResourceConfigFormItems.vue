<script setup lang="ts">
import type { CommonResourceConfig } from '@/api';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { NFlex, NFormItem, NInputNumber, NSelect } from 'naive-ui';
import { useStateStore } from '@/stores';
import { computed } from 'vue';
import { pickTranslation } from '@/utils';
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import { commonResourceConfigFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';

const model = defineModel<CommonResourceConfig>({ default: {} });
const state = useStateStore();

const categoryOptions = computed(
  () =>
    state.text?.resourceCategories?.map((c) => ({
      label:
        pickTranslation(c.translations, state.locale) ||
        `${c.key} (${$t('resources.settings.config.common.catUnlabelled')})`,
      value: c.key,
    })) || []
);

function handleUpdate(field: string, value: any) {
  model.value = {
    ...model.value,
    [field]: value,
  };
}
</script>

<template>
  <h4>{{ $t('resources.settings.config.common.heading') }}</h4>

  <!-- CATEGORY -->
  <n-form-item :label="$t('resources.settings.config.common.category')">
    <n-select
      :value="model.category"
      clearable
      :placeholder="$t('browse.uncategorized')"
      :options="categoryOptions"
      @update:value="(v) => handleUpdate('category', v)"
    />
  </n-form-item>

  <!-- SORT ORDER -->
  <n-form-item
    :label="$t('resources.settings.config.common.sortOrder')"
    path="config.common.sortOrder"
    :rule="commonResourceConfigFormRules.sortOrder"
  >
    <n-input-number
      :min="0"
      :max="999999"
      :value="model.sortOrder"
      style="width: 100%"
      @update:value="(v) => handleUpdate('sortOrder', v)"
    />
    <help-button-widget help-key="resourceSortOrder" gap-left />
  </n-form-item>

  <n-form-item :show-label="false" :show-feedback="false">
    <n-flex vertical>
      <!-- DEFAULT ACTIVE -->
      <labelled-switch
        :model-value="model.defaultActive"
        :label="$t('resources.settings.config.common.defaultActive')"
        @update:model-value="(v) => handleUpdate('defaultActive', v)"
      />
      <!-- SHOW ON PARENT LEVEL -->
      <n-flex :wrap="false" align="center">
        <labelled-switch
          :model-value="model.showOnParentLevel"
          :label="$t('resources.settings.config.common.showOnParentLevel')"
          @update:model-value="(u) => handleUpdate('showOnParentLevel', u)"
        />
        <help-button-widget help-key="resourceConfigCombinedSiblings" />
      </n-flex>
      <!-- QUICK SEARCHABLE -->
      <labelled-switch
        :model-value="model.quickSearchable"
        :label="$t('resources.settings.config.common.quickSearchable')"
        @update:model-value="(v) => handleUpdate('quickSearchable', v)"
      />
    </n-flex>
  </n-form-item>
</template>
