<script setup lang="ts">
import type { ItemDisplayProps, ItemGroup } from '@/api';
import { dynInputCreateBtnProps } from '@/common';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { commonResourceConfigFormRules } from '@/forms/formRules';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import { NDynamicInput, NFlex, NFormItem, NInput, NSelect, type FormItemRule } from 'naive-ui';
import { computed } from 'vue';

const props = defineProps<{
  groupsModelPath?: string;
  minGroups?: number;
  maxGroups?: number;
  displayPropsModelPath?: string;
  minDisplayProps?: number;
  maxDisplayProps?: number;
  itemNameRules?: FormItemRule[];
  groupNameLabel?: string;
  itemNameLabel?: string;
  existingItemNames?: string[];
  groupsHeading?: string;
  displayPropsHeading?: string;
  itemGroupingRequired?: boolean;
}>();

const groups = defineModel<ItemGroup[]>('groups', { required: true });
const displayProps = defineModel<ItemDisplayProps[]>('displayProps', { required: true });

const itemNameOptions = computed(() =>
  props.existingItemNames?.map((n) => ({ label: n, value: n }))
);
const itemGroupOptions = computed(() =>
  groups.value.map((g) => ({ label: g.name, value: g.name }))
);
</script>

<template>
  <form-section-heading :label="groupsHeading" />
  <n-form-item :show-label="false" :show-feedback="!!minGroups">
    <n-dynamic-input
      v-model:value="groups"
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
            :label="groupNameLabel || $t('general.name')"
            :path="`${groupsModelPath}[${index}].name`"
            :rule="commonResourceConfigFormRules.itemGroupNameRequired"
            style="flex: 1 200px"
          >
            <n-input v-model:value="groups[index].name" />
          </n-form-item>
          <!-- GROUP TRANSLATION -->
          <translation-form-item
            v-model="groups[index].translations"
            ignore-path-change
            secondary
            :parent-form-path-prefix="`${groupsModelPath}[${index}].translations`"
            style="flex: 2 100%"
            :main-form-label="$t('general.translation')"
            :translation-form-label="$t('general.translation', 2)"
            :translation-form-rules="commonResourceConfigFormRules.itemsDisplayTranslation"
          />
        </n-flex>
      </template>
      <template #action="{ index, create, remove, move }">
        <dynamic-input-controls
          top-offset
          :move-up-disabled="index === 0"
          :move-down-disabled="index === groups.length - 1"
          :insert-disabled="!!maxGroups && groups.length >= maxGroups"
          :remove-disabled="groups.length <= (minGroups || 0)"
          @move-up="() => move('up', index)"
          @move-down="() => move('down', index)"
          @remove="() => remove(index)"
          @insert="() => create(index)"
        />
      </template>
      <template #create-button-default>
        {{ $t('general.addAction') }}
      </template>
    </n-dynamic-input>
  </n-form-item>

  <form-section-heading :label="displayPropsHeading" />
  <n-form-item :show-label="false" :show-feedback="!!minDisplayProps">
    <n-dynamic-input
      v-model:value="displayProps"
      show-sort-button
      :min="minDisplayProps"
      :max="maxDisplayProps"
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
            :label="itemNameLabel || $t('general.key')"
            :path="`${displayPropsModelPath}[${index}].name`"
            :rule="commonResourceConfigFormRules.itemName"
            style="flex: 1 200px"
          >
            <n-select
              v-model:value="displayProps[index].name"
              tag
              filterable
              :options="itemNameOptions"
            />
          </n-form-item>
          <!-- ITEM TRANSLATION -->
          <translation-form-item
            v-model="displayProps[index].translations"
            ignore-path-change
            secondary
            :parent-form-path-prefix="`${displayPropsModelPath}[${index}].translations`"
            style="flex: 2 100%"
            :main-form-label="$t('general.translation', 2)"
            :translation-form-label="$t('general.translation')"
            :translation-form-rules="commonResourceConfigFormRules.itemsDisplayTranslation"
          />

          <!-- ITEM GROUP -->
          <n-form-item
            ignore-path-change
            :label="$t('general.group')"
            :path="`${displayPropsModelPath}[${index}].group`"
            :rule="
              itemGroupingRequired
                ? commonResourceConfigFormRules.itemGroupNameRequired
                : commonResourceConfigFormRules.itemGroupName
            "
            style="flex: 2 100%"
          >
            <n-select
              v-model:value="displayProps[index].group"
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
          :move-down-disabled="index === displayProps.length - 1"
          :insert-disabled="!!maxDisplayProps && displayProps.length >= maxDisplayProps"
          :remove-disabled="displayProps.length <= (minDisplayProps || 0)"
          @move-up="() => move('up', index)"
          @move-down="() => move('down', index)"
          @remove="() => remove(index)"
          @insert="() => create(index)"
        />
      </template>
      <template #create-button-default>
        {{ $t('general.addAction') }}
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>
