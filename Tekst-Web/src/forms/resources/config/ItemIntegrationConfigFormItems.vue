<script setup lang="ts">
import type { components } from '@/api/schema';
import { dynInputCreateBtnProps } from '@/common';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { commonResourceConfigFormRules } from '@/forms/formRules';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import { $t } from '@/i18n';
import { WandIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import {
  NButton,
  NDynamicInput,
  NFlex,
  NFormItem,
  NIcon,
  NInput,
  NSelect,
  type FormItemRule,
} from 'naive-ui';
import { computed } from 'vue';

const props = withDefaults(
  defineProps<{
    groupsModelPath?: string;
    minGroups?: number;
    maxGroups?: number;
    itemPropsModelPath?: string;
    minItemProps?: number;
    maxItemProps?: number;
    itemNameRules?: FormItemRule[];
    groupNameLabel?: string;
    itemNameLabel?: string;
    existingItemKeys?: string[];
    groupsHeading?: string;
    itemPropsHeading?: string | null;
    itemGroupingRequired?: boolean;
  }>(),
  {
    maxGroups: 64,
    maxItemProps: 128,
    itemPropsHeading: $t('resources.settings.config.itemIntegration.itemProps'),
  }
);

const model = defineModel<components['schemas']['ItemIntegrationConfig']>({ required: true });
const state = useStateStore();

const itemNameOptions = computed(() =>
  props.existingItemKeys?.map((n) => ({ label: n, value: n }))
);
const itemGroupOptions = computed(() =>
  model.value.groups.map((g) => ({
    label: `${g.key} (${pickTranslation(g.translations, state.locale)})`,
    value: g.key,
  }))
);

function generateItemProps() {
  if (!props.existingItemKeys?.length || !!model.value.itemProps.length) return;
  model.value.itemProps = props.existingItemKeys.map((k) => ({
    key: k,
    translations: [{ locale: '*', translation: k }],
  }));
}
</script>

<template>
  <!-- GROUPS -->
  <form-section-heading :label="groupsHeading" />
  <n-form-item :show-label="false" :show-feedback="!!minGroups">
    <n-dynamic-input
      v-model:value="model.groups"
      show-sort-button
      :min="minGroups"
      :max="maxGroups"
      :create-button-props="dynInputCreateBtnProps"
      @create="() => ({ name: undefined, translations: [{ locale: '*', translation: undefined }] })"
    >
      <template #default="{ index }">
        <n-flex align="flex-start" style="width: 100%">
          <!-- GROUP NAME -->
          <n-form-item
            ignore-path-change
            :label="groupNameLabel || $t('common.name')"
            :path="`${groupsModelPath}[${index}].key`"
            :rule="commonResourceConfigFormRules.itemGroupNameRequired"
            style="flex: 1 200px"
          >
            <n-input v-model:value="model.groups[index].key" />
          </n-form-item>
          <!-- GROUP TRANSLATION -->
          <translation-form-item
            v-model="model.groups[index].translations"
            ignore-path-change
            secondary
            :parent-form-path-prefix="`${groupsModelPath}[${index}].translations`"
            style="flex: 2 300px"
            :main-form-label="$t('common.translation')"
            :translation-form-label="$t('common.translation', 2)"
            :translation-form-rules="commonResourceConfigFormRules.itemsDisplayTranslation"
          />
        </n-flex>
      </template>
      <template #action="{ index, create, remove, move }">
        <dynamic-input-controls
          top-offset
          :move-up-disabled="index === 0"
          :move-down-disabled="index === model.groups.length - 1"
          :insert-disabled="!!maxGroups && model.groups.length >= maxGroups"
          :remove-disabled="model.groups.length <= (minGroups || 0)"
          @move-up="() => move('up', index)"
          @move-down="() => move('down', index)"
          @remove="() => remove(index)"
          @insert="() => create(index)"
        />
      </template>
      <template #create-button-default>
        {{ $t('common.add') }}
      </template>
    </n-dynamic-input>
  </n-form-item>

  <!-- ITEM PROPS -->
  <form-section-heading
    :show-label="itemPropsHeading !== null"
    :label="itemPropsHeading || undefined"
  />
  <!-- generate from existing item names -->
  <n-button
    v-if="!!existingItemKeys?.length && !model.itemProps.length"
    secondary
    block
    class="mb-sm"
    @click="generateItemProps"
  >
    <template #icon>
      <n-icon :component="WandIcon" />
    </template>
    {{ $t('resources.settings.config.itemIntegration.generateProps') }}
  </n-button>
  <n-form-item :show-label="false" :show-feedback="!!minItemProps">
    <n-dynamic-input
      v-model:value="model.itemProps"
      show-sort-button
      :min="minItemProps"
      :max="maxItemProps"
      :create-button-props="dynInputCreateBtnProps"
      @create="
        () => ({
          name: undefined,
          translations: [{ locale: '*', translation: undefined }],
          group: undefined,
        })
      "
    >
      <template #default="{ index }">
        <n-flex align="flex-start" style="width: 100%">
          <!-- ITEM NAME -->
          <n-form-item
            ignore-path-change
            :label="itemNameLabel || $t('common.key')"
            :path="`${itemPropsModelPath}[${index}].key`"
            :rule="commonResourceConfigFormRules.itemName"
            style="flex: 1 200px"
          >
            <n-select
              v-model:value="model.itemProps[index].key"
              tag
              filterable
              :options="itemNameOptions"
            />
          </n-form-item>
          <!-- ITEM TRANSLATION -->
          <translation-form-item
            v-model="model.itemProps[index].translations"
            ignore-path-change
            secondary
            :parent-form-path-prefix="`${itemPropsModelPath}[${index}].translations`"
            style="flex: 2 100%"
            :main-form-label="$t('common.translation', 2)"
            :translation-form-label="$t('common.translation')"
            :translation-form-rules="commonResourceConfigFormRules.itemsDisplayTranslation"
          />

          <!-- ITEM GROUP -->
          <n-form-item
            ignore-path-change
            :label="$t('common.group')"
            :path="`${itemPropsModelPath}[${index}].group`"
            :rule="
              itemGroupingRequired
                ? commonResourceConfigFormRules.itemGroupNameRequired
                : commonResourceConfigFormRules.itemGroupName
            "
            style="flex: 2 100%"
          >
            <n-select
              v-model:value="model.itemProps[index].group"
              tag
              filterable
              :options="itemGroupOptions"
            />
          </n-form-item>
        </n-flex>
      </template>
      <template #action="{ index, create, remove, move }">
        <dynamic-input-controls
          top-offset
          :move-up-disabled="index === 0"
          :move-down-disabled="index === model.itemProps.length - 1"
          :insert-disabled="!!maxItemProps && model.itemProps.length >= maxItemProps"
          :remove-disabled="model.itemProps.length <= (minItemProps || 0)"
          @move-up="() => move('up', index)"
          @move-down="() => move('down', index)"
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
