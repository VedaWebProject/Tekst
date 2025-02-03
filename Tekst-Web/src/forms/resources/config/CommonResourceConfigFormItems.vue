<script setup lang="ts">
import { type CommonResourceConfig, resourceTypes } from '@/api';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import { commonResourceConfigFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { NFlex, NFormItem, NInputNumber, NSelect } from 'naive-ui';
import { computed } from 'vue';

defineProps<{
  resourceType: string;
}>();

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

const oskOptions = computed(
  () =>
    state.pf?.state.oskModes?.map((oskMode) => ({
      label: oskMode.name,
      value: oskMode.key,
    })) || []
);

function handleUpdate(field: string, value: unknown) {
  model.value = {
    ...model.value,
    [field]: value,
  };
}
</script>

<template>
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

  <!-- PREFERRED OSK MODE -->
  <n-form-item :label="$t('osk.label')">
    <n-select
      :value="model.osk"
      clearable
      placeholder="–"
      :options="oskOptions"
      @update:value="(v) => handleUpdate('osk', v)"
    />
  </n-form-item>

  <!-- SORT ORDER -->
  <n-form-item path="config.common.sortOrder" :rule="commonResourceConfigFormRules.sortOrder">
    <template #label>
      <n-flex align="center" :wrap="false">
        {{ $t('resources.settings.config.common.sortOrder') }}
        <help-button-widget help-key="resourceSortOrder" />
      </n-flex>
    </template>
    <n-input-number
      :min="0"
      :max="1000"
      :value="model.sortOrder"
      style="width: 100%"
      @update:value="(v) => handleUpdate('sortOrder', v)"
    />
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
        :model-value="model.searchableQuick"
        :label="$t('resources.settings.config.common.searchableQuick')"
        :disabled="
          resourceTypes
            .filter((rt) => !rt.searchableQuick)
            .map((rt) => rt.name)
            .includes(resourceType)
        "
        @update:model-value="(v) => handleUpdate('searchableQuick', v)"
      />
      <!-- ADVANCED SEARCHABLE -->
      <labelled-switch
        :model-value="model.searchableAdv"
        :label="$t('resources.settings.config.common.searchableAdv')"
        :disabled="
          resourceTypes
            .filter((rt) => !rt.searchableAdv)
            .map((rt) => rt.name)
            .includes(resourceType)
        "
        @update:model-value="(v) => handleUpdate('searchableAdv', v)"
      />
      <!-- RIGHT-TO-LEFT TEXT DIRECTION -->
      <labelled-switch
        :model-value="model.rtl"
        :label="$t('resources.settings.config.common.rtl')"
        @update:model-value="(v) => handleUpdate('rtl', v)"
      />
    </n-flex>
  </n-form-item>
</template>
