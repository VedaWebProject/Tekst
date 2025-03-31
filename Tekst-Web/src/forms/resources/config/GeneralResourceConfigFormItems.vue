<script setup lang="ts">
import { type AnyResourceRead, type GeneralResourceConfig, resourceTypes } from '@/api';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import LabeledSwitch from '@/components/LabeledSwitch.vue';
import { commonResourceConfigFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { NFlex, NFormItem, NInputNumber, NSelect, type SelectOption } from 'naive-ui';
import { computed, h } from 'vue';

const props = defineProps<{
  resource: AnyResourceRead;
}>();

const model = defineModel<GeneralResourceConfig>({ default: {} });
const state = useStateStore();

const categoryOptions = computed(
  () =>
    state.text?.resourceCategories?.map((c) => ({
      label:
        pickTranslation(c.translations, state.locale) ||
        `${c.key} (${$t('resources.settings.config.general.catUnlabelled')})`,
      value: c.key,
    })) || []
);

const preventContentContext = computed(() =>
  resourceTypes
    .filter((rt) => !rt.contentContext)
    .map((rt) => rt.name)
    .includes(props.resource.resourceType)
);

const preventQuickSearchable = computed(() =>
  resourceTypes
    .filter((rt) => !rt.searchableQuick)
    .map((rt) => rt.name)
    .includes(props.resource.resourceType)
);

const preventAdvSearchable = computed(() =>
  resourceTypes
    .filter((rt) => !rt.searchableAdv)
    .map((rt) => rt.name)
    .includes(props.resource.resourceType)
);

const oskOptions = computed(
  () =>
    state.pf?.state.oskModes?.map((oskMode) => ({
      label: oskMode.name,
      value: oskMode.key,
    })) || []
);

const fontOptions = computed(() =>
  [...(state.pf?.state.fonts || []), 'Tekst Content Font', 'Tekst UI Font']?.map((f) => ({
    label: f,
    value: f,
  }))
);

function renderFontLabel(option: SelectOption) {
  return h(
    'div',
    {
      style: `font-family: '${option.value}', 'Tekst Content Font', serif;`,
    },
    option.label as string
  );
}
</script>

<template>
  <form-section-heading :label="$t('common.general')" />

  <!-- CATEGORY -->
  <n-form-item :label="$t('resources.settings.config.general.category')">
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
        {{ $t('resources.settings.config.general.sortOrder') }}
        <help-button-widget help-key="resourceSortOrder" />
      </n-flex>
    </template>
    <n-input-number v-model:value="model.sortOrder" :min="0" :max="1000" style="width: 100%" />
  </n-form-item>

  <!-- CONTENT FONT -->
  <n-form-item :label="$t('resources.settings.config.general.font')">
    <n-select
      v-model:value="model.font"
      clearable
      :options="fontOptions"
      :placeholder="$t('common.default')"
      :render-label="renderFontLabel"
    />
  </n-form-item>

  <!-- DEFAULT ACTIVE -->
  <n-form-item :show-label="false" :show-feedback="false">
    <labeled-switch
      v-model="model.defaultActive"
      :label="$t('resources.settings.config.general.defaultActive')"
    />
  </n-form-item>

  <!-- ENABLE CONTENT CONTEXT -->
  <n-form-item :show-label="false" :show-feedback="false">
    <n-flex :wrap="false" align="center">
      <labeled-switch
        v-model="model.enableContentContext"
        :label="$t('resources.settings.config.general.enableContentContext')"
        :disabled="preventContentContext"
      />
      <help-button-widget help-key="resourceConfigCombinedSiblings" />
    </n-flex>
  </n-form-item>

  <!-- QUICK SEARCHABLE -->
  <n-form-item :show-label="false" :show-feedback="false">
    <labeled-switch
      v-model="model.searchableQuick"
      :label="$t('resources.settings.config.general.searchableQuick')"
      :disabled="preventQuickSearchable"
    />
  </n-form-item>

  <!-- ADVANCED SEARCHABLE -->
  <n-form-item :show-label="false" :show-feedback="false">
    <labeled-switch
      v-model="model.searchableAdv"
      :label="$t('resources.settings.config.general.searchableAdv')"
      :disabled="preventAdvSearchable"
    />
  </n-form-item>

  <!-- COLLAPSIBLE CONTENTS -->
  <n-form-item :show-label="false" :show-feedback="false">
    <labeled-switch
      v-model="model.defaultCollapsed"
      :label="$t('resources.settings.config.general.defaultCollapsed')"
    />
  </n-form-item>

  <!-- RIGHT-TO-LEFT TEXT DIRECTION -->
  <n-form-item :show-label="false" :show-feedback="false">
    <labeled-switch v-model="model.rtl" :label="$t('resources.settings.config.general.rtl')" />
  </n-form-item>
</template>
