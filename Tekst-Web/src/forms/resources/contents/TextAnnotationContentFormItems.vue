<script setup lang="ts">
import type {
  AnnotationAggregation,
  TextAnnotationContentCreate,
  TextAnnotationResourceRead,
} from '@/api';
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import NInputOsk from '@/components/NInputOsk.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { contentFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { KeyboardReturnIcon } from '@/icons';
import { useResourcesStore } from '@/stores';
import { NDynamicInput, NFormItem, NSelect, type SelectOption } from 'naive-ui';
import { computed, h, onMounted, ref } from 'vue';

const props = defineProps<{
  resource: TextAnnotationResourceRead;
}>();
const model = defineModel<TextAnnotationContentCreate>({ required: true });
const tokenInputRefs = ref<{ [key: number]: InstanceType<typeof NInputOsk> }>({});

const resources = useResourcesStore();

const annoValueStyle = {
  fontFamily: props.resource.config.general.font || 'Tekst Content Font',
};

const aggregations = ref<AnnotationAggregation[]>([]);
const annoOptions = computed(() => {
  // all possible keys, containing unique keys collected in
  // aggregations and from the current model state
  const keys = [
    ...new Set([
      ...aggregations.value.map((agg) => agg.key),
      ...model.value.tokens.map((t) => t.annotations.map((a) => a.key) || []).flat(),
    ]),
  ];
  return model.value.tokens.map(
    (t) =>
      t.annotations.map((a) => ({
        keysOptions: keys
          .filter((k) => !t.annotations.map((a) => a.key).includes(k))
          .map((k) => ({
            label: k,
            value: k,
          })),
        valuesOptions:
          aggregations.value
            .find((agg) => agg.key === a.key)
            ?.values?.map((v) => ({ label: v, value: v })) || [],
      })) || []
  );
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

function handleUpdate(field: string, value: unknown) {
  model.value = {
    ...model.value,
    [field]: value,
  };
}

onMounted(async () => {
  aggregations.value = await resources.getAggregations(props.resource.id);
});
</script>

<template>
  <!-- TOKENS -->
  <n-form-item :show-label="false" :show-feedback="false">
    <n-dynamic-input
      :value="model.tokens"
      :min="1"
      :max="1024"
      @create="handleInsertToken"
      @update:value="(value) => handleUpdate('tokens', value)"
    >
      <template #default="{ value: tokenItem, index: tokenItemIndex }">
        <div
          style="
            display: flex;
            align-items: flex-start;
            gap: var(--gap-md);
            flex-grow: 2;
            flex-wrap: wrap;
          "
        >
          <div
            style="
              flex-grow: 1;
              flex-basis: 250px;
              display: flex;
              align-items: flex-start;
              gap: var(--gap-md);
              flex-wrap: nowrap;
            "
          >
            <!-- TOKEN -->
            <n-form-item
              :label="$t('resources.types.textAnnotation.contentFields.token')"
              :path="`tokens[${tokenItemIndex}].token`"
              :rule="contentFormRules.textAnnotation.token"
              ignore-path-change
              style="flex-grow: 2"
            >
              <n-input-osk
                :ref="
                  (el) => (tokenInputRefs[tokenItemIndex] = el as InstanceType<typeof NInputOsk>)
                "
                v-model="tokenItem.token"
                :font="resource.config.general.font || undefined"
                :osk-key="resource.config.common.osk || undefined"
                :placeholder="$t('resources.types.textAnnotation.contentFields.token')"
              />
            </n-form-item>
            <!-- LINEBREAK -->
            <n-form-item ignore-path-change>
              <labelled-switch
                v-model="tokenItem.lb"
                size="large"
                :icon-on="KeyboardReturnIcon"
                :icon-off="KeyboardReturnIcon"
                :title="$t('resources.types.textAnnotation.contentFields.lb')"
              />
            </n-form-item>
          </div>
          <!-- ANNOTATIONS -->
          <n-form-item
            :label="$t('resources.types.textAnnotation.contentFields.annotations')"
            :show-feedback="false"
            :path="`tokens[${tokenItemIndex}].annotations`"
            style="flex-grow: 2; flex-basis: 400px"
          >
            <n-dynamic-input
              v-model:value="tokenItem.annotations"
              @create="() => ({ key: undefined, value: undefined })"
            >
              <template #default="{ value: annotationItem, index: annotationItemIndex }">
                <div
                  style="
                    display: flex;
                    flex-wrap: nowrap;
                    flex-grow: 2;
                    gap: var(--gap-md);
                    align-items: flex-start;
                  "
                >
                  <n-form-item
                    style="flex-grow: 2; flex-basis: 100px"
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
                  <n-form-item
                    style="flex-grow: 2; flex-basis: 100px"
                    :show-label="false"
                    :path="`tokens[${tokenItemIndex}].annotations[${annotationItemIndex}].value`"
                    :rule="contentFormRules.textAnnotation.annotationValue"
                    ignore-path-change
                  >
                    <n-select
                      v-model:value="annotationItem.value"
                      multiple
                      filterable
                      tag
                      clearable
                      :disabled="!annotationItem.key"
                      :options="annoOptions[tokenItemIndex][annotationItemIndex].valuesOptions"
                      :placeholder="$t('general.value')"
                      :style="annoValueStyle"
                      :render-label="renderValueLabel"
                    />
                  </n-form-item>
                </div>
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
                  :insert-disabled="annotationActionIndex >= 127"
                  @remove="() => removeAnnotation(annotationActionIndex)"
                  @insert="() => createAnnotation(annotationActionIndex)"
                />
              </template>
            </n-dynamic-input>
          </n-form-item>
        </div>
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
