<script setup lang="ts">
import type {
  KeyValueAggregations,
  TextAnnotationResourceRead,
  TextAnnotationSearchQuery,
} from '@/api';
import { dynInputCreateBtnProps } from '@/common';
import { usePrompt } from '@/composables/prompt';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { searchFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { AsteriskIcon, InfoIcon, KeyboardIcon } from '@/icons';
import { useResourcesStore, useStateStore } from '@/stores';
import { groupAndSortItems, pickTranslation } from '@/utils';
import { NButton, NDynamicInput, NFlex, NFormItem, NIcon, NSelect } from 'naive-ui';
import { computed, onMounted, ref } from 'vue';

const _V_EXISTS = '#!V_EXISTS!#';
const _V_MISSING = '#!V_MISSING!#';

const props = defineProps<{
  resource: TextAnnotationResourceRead;
  queryIndex: number;
}>();
const model = defineModel<TextAnnotationSearchQuery>({ required: true });

const state = useStateStore();
const resources = useResourcesStore();
const prompt = usePrompt();

const annoValueStyle = {
  fontFamily: props.resource.config.general.font || 'var(--font-family-content)',
};

const aggregations = ref<KeyValueAggregations>([]);
const annoOptions = computed(() => {
  const itemCfg = props.resource.config.special.annotations.annoIntegration;

  // generate general key options
  const keysOptions = groupAndSortItems(
    aggregations.value.map((agg) => ({ key: agg.key, value: agg.values })),
    itemCfg
  ).map((group, i) => ({
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
        label: lbl || item.key,
        value: item.key,
      };
    }),
  }));

  // generate key and value select options
  const options = (model.value.anno || []).map((a) => ({
    keysOptions: keysOptions.map((group) => ({
      ...group,
      // disable children that are already in use
      children: group.children.map((c) => ({
        ...c,
        disabled: !!model.value.anno?.map((an) => an.k).includes(c.value),
      })),
    })),
    valuesOptions: [
      // "exists" value option
      {
        label: () => `[${$t('search.advancedSearch.values.exists')}]`,
        value: _V_EXISTS,
        disabled: !!model.value.anno
          ?.filter((an) => an.k === a.k)
          .map((an) => an.v)
          .flat()
          ?.includes(_V_MISSING),
      },
      // "missing" value option
      {
        label: () => `[${$t('search.advancedSearch.values.missing')}]`,
        value: _V_MISSING,
        disabled: !!model.value.anno
          ?.filter((an) => an.k === a.k)
          .map((an) => an.v)
          .flat()
          ?.includes(_V_EXISTS),
      },
      // existing values from aggregations
      ...(aggregations.value
        // find possible values for the selected key
        .find((agg) => agg.key === a.k)
        ?.values // map anno key-value pairs to options
        ?.map((v) => ({
          label: v,
          value: v,
          disabled:
            !!model.value.anno
              ?.filter((an) => an.k === a.k)
              .map((an) => an.v)
              .flat()
              ?.includes(_V_EXISTS) ||
            !!model.value.anno
              ?.filter((an) => an.k === a.k)
              .map((an) => an.v)
              .flat()
              ?.includes(_V_MISSING),
          style: annoValueStyle,
        })) || []),
    ],
  }));

  return options;
});

function getAnnoValueSelectStyle(value?: string) {
  return value ? annoValueStyle : undefined;
}

function validateValueSelections() {
  model.value.anno?.forEach((anno) => {
    if (!!anno.v?.includes(_V_EXISTS)) {
      anno.v = [_V_EXISTS];
      anno.spc = 'exists';
    } else if (!!anno.v?.includes(_V_MISSING)) {
      anno.v = [_V_MISSING];
      anno.spc = 'missing';
    } else {
      delete anno.spc;
    }
  });
}

async function handleFreeFormInput(annotationItem: NonNullable<typeof model.value.anno>[number]) {
  const annoValueInput = await prompt({
    type: 'singleLineInputOSK',
    icon: KeyboardIcon,
    title: $t('common.annotation') + ': ' + $t('common.value'),
    label: $t('common.value'),
    msg: $t('resources.types.textAnnotation.contentFields.commaSepHint'),
    font: props.resource.contentFont,
  });
  if (!annoValueInput) return;
  if (!Array.isArray(annotationItem.v)) {
    annotationItem.v = (annotationItem.v ?? '').split(/[\s\n]*,[\s\n]*/g);
  }
  annotationItem.v = [
    ...annotationItem.v.filter((v) => v != null),
    ...annoValueInput.split(/[\s\n]*,[\s\n]*/g),
  ].map((v) => v.trim());
}

onMounted(async () => {
  model.value.anno = model.value.anno || [{ k: '', v: undefined, wc: false }];
  aggregations.value = await resources.getAggregations(props.resource.id);
});
</script>

<template>
  <!-- ANNOTATIONS -->
  <n-form-item
    :label="$t('common.annotation', 2)"
    :show-feedback="!model.anno?.length"
    style="flex: 2 400px"
  >
    <n-dynamic-input
      v-model:value="model.anno"
      :create-button-props="dynInputCreateBtnProps"
      @create="() => ({ k: undefined, v: undefined })"
    >
      <template #default="{ value: annotationItem, index: annotationItemIndex }">
        <n-flex wrap align="flex-start" style="flex: 2">
          <!-- KEY -->
          <n-form-item
            style="flex: 2 200px"
            :show-label="false"
            :show-feedback="false"
            ignore-path-change
            :path="`queries[${queryIndex}].rts.anno[${annotationItemIndex}].k`"
          >
            <n-select
              v-model:value="annotationItem.k"
              filterable
              clearable
              :options="annoOptions[annotationItemIndex].keysOptions"
              :placeholder="$t('common.annotation')"
              @update:value="() => (annotationItem.v = '')"
            />
          </n-form-item>

          <n-flex :wrap="false" align="flex-start" style="flex: 2 248px">
            <!-- VALUE -->
            <n-form-item
              :show-label="false"
              ignore-path-change
              :path="`queries[${queryIndex}].rts.anno[${annotationItemIndex}].v`"
              :rule="searchFormRules.textAnnotation.annotationValue"
              style="flex: 2 200px"
            >
              <n-select
                v-model:value="annotationItem.v"
                filterable
                clearable
                tag
                multiple
                :disabled="!annotationItem.k"
                :style="getAnnoValueSelectStyle(annotationItem.v)"
                :options="annoOptions[annotationItemIndex].valuesOptions"
                :placeholder="$t('common.value')"
                class="taggable-select"
                @update:value="validateValueSelections"
              >
                <template #header>
                  <n-flex align="baseline" class="text-small translucent" :wrap="false">
                    <n-icon :component="InfoIcon" />
                    {{ $t('resources.types.textAnnotation.contentFields.valueEnterHint') }}
                  </n-flex>
                </template>
              </n-select>
            </n-form-item>

            <!-- USE OSK FOR INPUT -->
            <n-form-item :show-label="false">
              <n-button
                secondary
                :disabled="
                  !annotationItem.k ||
                  annotationItem.v.includes(_V_EXISTS) ||
                  annotationItem.v.includes(_V_MISSING)
                "
                :title="$t('osk.label')"
                @click="handleFreeFormInput(annotationItem)"
              >
                <template #icon>
                  <n-icon :component="KeyboardIcon" />
                </template>
              </n-button>
            </n-form-item>

            <!-- VALUE QUERY WILDCARDS -->
            <n-form-item ignore-path-change :show-label="false">
              <n-button
                secondary
                :type="annotationItem.wc ? 'success' : undefined"
                :disabled="
                  !annotationItem.k ||
                  annotationItem.v.includes(_V_EXISTS) ||
                  annotationItem.v.includes(_V_MISSING)
                "
                :title="$t('search.advancedSearch.wc')"
                @click="annotationItem.wc = !annotationItem.wc"
              >
                <template #icon>
                  <n-icon :component="AsteriskIcon" />
                </template>
              </n-button>
            </n-form-item>
          </n-flex>
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
          :movable="false"
          :insert-disabled="annotationActionIndex >= 63"
          @remove="() => removeAnnotation(annotationActionIndex)"
          @insert="() => createAnnotation(annotationActionIndex)"
        />
      </template>
      <template #create-button-default>
        {{ $t('common.select') }}
      </template>
    </n-dynamic-input>
  </n-form-item>
</template>
