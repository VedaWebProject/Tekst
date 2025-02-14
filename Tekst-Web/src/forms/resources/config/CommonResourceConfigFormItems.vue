<script setup lang="ts">
import { type CommonResourceConfig, resourceTypes } from '@/api';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import LabeledSwitch from '@/components/LabeledSwitch.vue';
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
</script>

<template>
  <form-section-heading :label="$t('resources.settings.integration')" />

  <!-- CATEGORY -->
  <n-form-item :label="$t('resources.settings.config.common.category')">
    <n-select
      v-model:value="model.category"
      clearable
      :placeholder="$t('browse.uncategorized')"
      :options="categoryOptions"
    />
  </n-form-item>

  <!-- PREFERRED OSK MODE -->
  <n-form-item :label="$t('osk.label')">
    <n-select v-model:value="model.osk" clearable placeholder="–" :options="oskOptions" />
  </n-form-item>

  <!-- SORT ORDER -->
  <n-form-item path="config.common.sortOrder" :rule="commonResourceConfigFormRules.sortOrder">
    <template #label>
      <n-flex align="center" :wrap="false">
        {{ $t('resources.settings.config.common.sortOrder') }}
        <help-button-widget help-key="resourceSortOrder" />
      </n-flex>
    </template>
    <n-input-number v-model:value="model.sortOrder" :min="0" :max="1000" style="width: 100%" />
  </n-form-item>

  <!-- DEFAULT ACTIVE -->
  <n-form-item :show-label="false" :show-feedback="false">
    <labeled-switch
      v-model="model.defaultActive"
      :label="$t('resources.settings.config.common.defaultActive')"
    />
  </n-form-item>

  <!-- SHOW ON PARENT LEVEL -->
  <n-form-item :show-label="false" :show-feedback="false">
    <n-flex :wrap="false" align="center">
      <labeled-switch
        v-model="model.showOnParentLevel"
        :label="$t('resources.settings.config.common.showOnParentLevel')"
        :disabled="
          resourceTypes
            .filter((rt) => !rt.contentContext)
            .map((rt) => rt.name)
            .includes(resourceType)
        "
      />
      <help-button-widget help-key="resourceConfigCombinedSiblings" />
    </n-flex>
  </n-form-item>

  <!-- QUICK SEARCHABLE -->
  <n-form-item :show-label="false" :show-feedback="false">
    <labeled-switch
      v-model="model.searchableQuick"
      :label="$t('resources.settings.config.common.searchableQuick')"
      :disabled="
        resourceTypes
          .filter((rt) => !rt.searchableQuick)
          .map((rt) => rt.name)
          .includes(resourceType)
      "
    />
  </n-form-item>

  <!-- ADVANCED SEARCHABLE -->
  <n-form-item :show-label="false">
    <labeled-switch
      v-model="model.searchableAdv"
      :label="$t('resources.settings.config.common.searchableAdv')"
      :disabled="
        resourceTypes
          .filter((rt) => !rt.searchableAdv)
          .map((rt) => rt.name)
          .includes(resourceType)
      "
    />
  </n-form-item>

  <form-section-heading :label="$t('resources.settings.config.common.rtl.heading')" />

  <!-- RIGHT-TO-LEFT TEXT DIRECTION -->
  <n-form-item :show-label="false">
    <labeled-switch
      v-model="model.rtl"
      :on-label="$t('resources.settings.config.common.rtl.rtl')"
      :off-label="$t('resources.settings.config.common.rtl.ltr')"
    />
  </n-form-item>
</template>
