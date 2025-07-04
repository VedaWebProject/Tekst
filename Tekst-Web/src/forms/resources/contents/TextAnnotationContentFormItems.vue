<script setup lang="ts">
import type {
  KeyValueAggregations,
  TextAnnotationContentCreate,
  TextAnnotationResourceRead,
} from '@/api';
import { dynInputCreateBtnProps } from '@/common';
import OskInput from '@/components/OskInput.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { contentFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { useResourcesStore, useStateStore } from '@/stores';
import { groupAndSortItems, pickTranslation } from '@/utils';
import { NDynamicInput, NFlex, NFormItem, NInput, NSelect, type SelectOption } from 'naive-ui';
import { computed, h, onMounted, ref } from 'vue';

const props = defineProps<{
  resource: TextAnnotationResourceRead;
}>();
const model = defineModel<TextAnnotationContentCreate>({ required: true });
const tokenInputRefs = ref<{ [key: number]: InstanceType<typeof OskInput> }>({});

const state = useStateStore();
const resources = useResourcesStore();

const annoValueStyle = {
  fontFamily: props.resource.config.general.font || 'var(--font-family-content)',
};

const aggregations = ref<KeyValueAggregations>([]);
const annoOptions = computed(() => {
  // all possible keys, containing unique keys collected in
  // aggregations and from the current model state
  const itemCfg = props.resource.config.special.annotations.annoIntegration;
  const keys = aggregations.value
    .map((agg) => ({ key: agg.key, value: agg.values }))
    .concat(
      model.value.tokens
        .map((t) => t.annotations || [])
        .flat()
        .filter((a) => !aggregations.value.map((agg) => agg.key).includes(a.key))
    );

  // generate general key options
  const keysOptions = groupAndSortItems(keys, itemCfg).map((group, i) => ({
    label:
      pickTranslation(
        itemCfg.groups.find((g) => g.key === group.group)?.translations,
        state.locale
      ) ||
      group.group ||
      $t('common.other'),
    type: 'group',
    key: `$group_${i}_${group.group || 'ungrouped'}`,
    children: group.items.map((item) => {
      const lbl =
        pickTranslation(
          itemCfg.itemProps.find((p) => p.key === item.key)?.translations,
          state.locale
        ) || item.key;
      return {
        label: `${item.key} (${lbl})`,
        value: item.key,
      };
    }),
  }));

  // generate key and value select options for each token
  const options = model.value.tokens.map(
    (t) =>
      t.annotations.map((a) => ({
        keysOptions: keysOptions.map((group) => ({
          ...group,
          children: group.children.map((c) => ({
            ...c,
            // disable options that are already selected
            disabled: t.annotations?.map((an) => an.key).includes(c.value),
          })),
        })),
        // existing values from aggregations, filtered for the selected key
        valuesOptions:
          aggregations.value
            .find((agg) => agg.key === a.key)
            ?.values?.map((v) => ({ label: v, value: v })) || [],
      })) || []
  );

  return options;
});

function renderValueLabel(option: SelectOption) {
  return h(
    'div',
    {
      style: annoValueStyle,
    },
    option.label as string
  );
}

function handleInsertToken(index: number) {
  setTimeout(() => {
    tokenInputRefs.value[index]?.focus();
  }, 100);
  return { token: undefined, annotations: [] };
}

onMounted(async () => {
  aggregations.value = await resources.getAggregations(props.resource.id);
});
</script>

<template>
  <!-- TOKENS -->
  <n-form-item :show-label="false" :show-feedback="false">
    <n-dynamic-input
      v-model:value="model.tokens"
      :min="1"
      :max="1024"
      :create-button-props="dynInputCreateBtnProps"
      item-class="divided"
      @create="handleInsertToken"
    >
      <template #default="{ value: tokenItem, index: tokenItemIndex }">
        <n-flex align="flex-start" style="flex: 2">
          <!-- ANNOTATIONS -->
          <n-form-item
            :label="$t('resources.types.textAnnotation.contentFields.annotations')"
            :show-feedback="false"
            :path="`tokens[${tokenItemIndex}].annotations`"
            style="flex: 2 400px"
          >
            <n-dynamic-input
              v-model:value="tokenItem.annotations"
              :create-button-props="dynInputCreateBtnProps"
              @create="() => ({ key: undefined, value: undefined })"
            >
              <template #default="{ value: annotationItem, index: annotationItemIndex }">
                <n-flex align="flex-start" style="flex: 2">
                  <!-- KEY -->
                  <n-form-item
                    style="flex: 2 180px"
                    :show-label="false"
                    :path="`tokens[${tokenItemIndex}].annotations[${annotationItemIndex}].key`"
                    :rule="contentFormRules.textAnnotation.annotationKey"
                    ignore-path-change
                  >
                    <n-select
                      v-model:value="annotationItem.key"
                      filterable
                      tag
                      clearable
                      :options="annoOptions[tokenItemIndex][annotationItemIndex].keysOptions"
                      :placeholder="
                        $t('resources.types.textAnnotation.contentFields.annotationKey')
                      "
                      @update:value="() => (annotationItem.value = '')"
                    />
                  </n-form-item>
                  <!-- VALUES -->
                  <n-form-item
                    style="flex: 2 180px"
                    :show-label="false"
                    :path="`tokens[${tokenItemIndex}].annotations[${annotationItemIndex}].value`"
                    :rule="contentFormRules.textAnnotation.annotationValue"
                    ignore-path-change
                  >
                    <n-select
                      v-if="!!annoOptions[tokenItemIndex][annotationItemIndex].valuesOptions.length"
                      v-model:value="annotationItem.value"
                      multiple
                      filterable
                      tag
                      clearable
                      :disabled="!annotationItem.key"
                      :options="annoOptions[tokenItemIndex][annotationItemIndex].valuesOptions"
                      :placeholder="$t('common.value')"
                      :style="annoValueStyle"
                      :render-label="renderValueLabel"
                    />
                    <n-input
                      v-else
                      :ref="`cmSepInputRef_${tokenItemIndex}_${annotationItemIndex}`"
                      :default-value="(annotationItem.value || []).join(', ')"
                      :disabled="!annotationItem.key"
                      :placeholder="$t('resources.types.textAnnotation.contentFields.commaSepHint')"
                      :title="$t('resources.types.textAnnotation.contentFields.commaSepHint')"
                      @change="
                        (value) => (annotationItem.value = value.split(',').map((v) => v.trim()))
                      "
                    />
                  </n-form-item>
                </n-flex>
              </template>
              <template
                #action="{
                  index: annotationActionIndex,
                  create: createAnnotation,
                  remove: removeAnnotation,
                }"
              >
                <dynamic-input-controls
                  secondary
                  :movable="false"
                  :insert-disabled="tokenItem.annotations.length >= 128"
                  @remove="() => removeAnnotation(annotationActionIndex)"
                  @insert="() => createAnnotation(annotationActionIndex)"
                />
              </template>
              <template #create-button-default>
                {{ $t('common.add') }}
              </template>
            </n-dynamic-input>
          </n-form-item>
        </n-flex>
      </template>
      <template
        #action="{
          index: tokenActionIndex,
          create: createTokenItem,
          remove: removeTokenItem,
          move: moveTokenItem,
        }"
      >
        <dynamic-input-controls
          top-offset
          :move-up-disabled="tokenActionIndex === 0"
          :move-down-disabled="tokenActionIndex === model.tokens.length - 1"
          :remove-disabled="model.tokens.length <= 1"
          :insert-disabled="model.tokens.length >= 1024"
          @move-up="() => moveTokenItem('up', tokenActionIndex)"
          @move-down="() => moveTokenItem('down', tokenActionIndex)"
          @remove="() => removeTokenItem(tokenActionIndex)"
          @insert="() => createTokenItem(tokenActionIndex)"
        />
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>
