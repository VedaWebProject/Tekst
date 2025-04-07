<script setup lang="ts">
import { type AnyResourceRead, type GeneralResourceConfig, resourceTypes } from '@/api';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import LabeledSwitch from '@/components/LabeledSwitch.vue';
import { commonResourceConfigFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { NFlex, NFormItem, NInputNumber, NSelect, NSlider, type SelectOption } from 'naive-ui';
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
  [...(state.pf?.state.fonts || []), 'Tekst Content Font', 'Tekst UI Font']
    .filter((f) => !!f)
    .map((f) => ({
      label: f,
      value: f,
    }))
);

const cCMarks = {
  0: () => renderCCMark(0),
  200: () => renderCCMark(200),
  400: () => renderCCMark(400),
  600: () => renderCCMark(600),
  800: () => renderCCMark(800),
};

function renderFontLabel(option: SelectOption) {
  const fontIsValid = !!option.value && !!state.pf?.state.fonts?.includes(option.value as string);
  return h(
    'div',
    {
      style: {fontFamily: [option.value, 'var(--font-family-content)'].filter((f) => !!f).join(', '),
      color: !fontIsValid ? 'var(--error-color)' : undefined,
      textDecoration: !fontIsValid ? 'line-through' : undefined,}
    },
    option.label as string
  );
}

function renderCCMark(value: number) {
  return h(
    'span',
    { class: { 'text-tiny': true, b: value === 0 } },
    value > 0 ? `${value}px` : $t('common.off')
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
  <n-form-item path="config.general.sortOrder" :rule="commonResourceConfigFormRules.sortOrder">
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

  <!-- RIGHT-TO-LEFT TEXT DIRECTION -->
  <n-form-item :show-label="false">
    <labeled-switch v-model="model.rtl" :label="$t('resources.settings.config.general.rtl')" />
  </n-form-item>

  <!-- COLLAPSIBLE CONTENTS -->
  <n-form-item :label="$t('resources.settings.config.general.collapsibleContents')">
    <n-slider
      :value="model.collapsibleContents || 0"
      :marks="cCMarks"
      step="mark"
      :min="0"
      :max="800"
      :format-tooltip="(v) => (v > 0 ? `${v}px` : $t('common.off'))"
      style="width: 98%"
      @update:value="(v) => (model.collapsibleContents = v > 0 ? v : null)"
    />
  </n-form-item>
</template>
