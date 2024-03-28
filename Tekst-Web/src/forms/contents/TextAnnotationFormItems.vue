<script setup lang="ts">
import type { TextAnnotationContentCreate } from '@/api';
import NInputOsk from '@/components/NInputOsk.vue';
import { AddIcon, ArrowDownIcon, ArrowUpIcon, MinusIcon } from '@/icons';
import {
  NAlert,
  NSelect,
  NFormItem,
  NButton,
  NDynamicInput,
  NSpace,
  NIcon,
  NButtonGroup,
} from 'naive-ui';
import { contentFormRules } from '../formRules';
import { useStateStore } from '@/stores';

const props = defineProps<{
  model?: TextAnnotationContentCreate;
}>();

const emit = defineEmits(['update:model']);

const state = useStateStore();

function handleUpdate(field: string, value: any) {
  emit('update:model', {
    ...props.model,
    [field]: value,
  });
}
</script>

<template>
  <template v-if="model">
    <!-- TOKENIZE UTIL -->
    <n-alert style="margin-bottom: var(--layout-gap)">
      <n-space justify="end">
        <n-button secondary title="TOKENIZE">
          <template #icon>
            <n-icon :component="MinusIcon" />
            <!-- <n-icon :component="HorizontalDistributeOutlined" /> -->
          </template>
          TOKENIZE!!
        </n-button>
      </n-space>
    </n-alert>
    <!-- TOKENS -->
    <n-form-item :show-label="false" :show-feedback="false">
      <n-dynamic-input
        :value="model.tokens"
        :min="1"
        :max="1024"
        @create="() => ({ token: undefined, annotations: [] })"
        @update:value="(value) => handleUpdate('tokens', value)"
      >
        <template #default="{ value: tokenItem, index: tokenItemIndex }">
          <div
            style="
              display: flex;
              align-items: flex-start;
              gap: var(--content-gap);
              flex-grow: 2;
              flex-wrap: wrap;
            "
          >
            <!-- TOKEN -->
            <n-form-item
              :label="$t('resources.types.textAnnotation.contentFields.token')"
              :path="`tokens[${tokenItemIndex}].token`"
              :rule="contentFormRules.textAnnotation.token"
              ignore-path-change
              style="flex-grow: 1; flex-basis: 200px"
            >
              <n-input-osk
                v-model:value="tokenItem.token"
                :placeholder="$t('resources.types.textAnnotation.contentFields.token')"
              />
            </n-form-item>
            <!-- ANNOTATIONS -->
            <n-form-item
              :label="$t('resources.types.textAnnotation.contentFields.annotations')"
              :show-feedback="false"
              :path="`tokens[${tokenItemIndex}].annotations`"
              style="flex-grow: 2; flex-basis: 400px"
            >
              <n-dynamic-input
                v-model:value="tokenItem.annotations"
                :max="128"
                @create="() => ({ key: undefined, value: undefined })"
              >
                <template #default="{ value: annotationItem, index: annotationItemIndex }">
                  <div
                    style="
                      display: flex;
                      flex-wrap: nowrap;
                      flex-grow: 2;
                      gap: var(--content-gap);
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
                        :options="[]"
                        :placeholder="
                          $t('resources.types.textAnnotation.contentFields.annotationKey')
                        "
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
                        filterable
                        tag
                        clearable
                        :disabled="!annotationItem.key"
                        :options="[]"
                        :placeholder="
                          $t('resources.types.textAnnotation.contentFields.annotationValue')
                        "
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
                  <n-space style="margin-left: var(--content-gap)">
                    <n-button-group>
                      <n-button
                        quaternary
                        :focusable="false"
                        :title="$t('general.removeAction')"
                        @click="() => removeAnnotation(annotationActionIndex)"
                      >
                        <template #icon>
                          <n-icon :component="MinusIcon" />
                        </template>
                      </n-button>
                      <n-button
                        quaternary
                        :focusable="false"
                        :title="$t('general.insertAction')"
                        @click="() => createAnnotation(annotationActionIndex)"
                      >
                        <template #icon>
                          <n-icon :component="AddIcon" />
                        </template>
                      </n-button>
                    </n-button-group>
                  </n-space>
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
          <n-button-group
            :vertical="state.smallScreen"
            style="margin-left: var(--content-gap); padding-top: 26px"
          >
            <n-button
              type="primary"
              secondary
              :title="$t('general.moveUpAction')"
              :disabled="tokenActionIndex === 0"
              :focusable="false"
              @click="() => moveTokenItem('up', tokenActionIndex)"
            >
              <template #icon>
                <n-icon :component="ArrowUpIcon" />
              </template>
            </n-button>
            <n-button
              type="primary"
              secondary
              :title="$t('general.moveDownAction')"
              :disabled="tokenActionIndex === model.tokens.length - 1"
              :focusable="false"
              @click="() => moveTokenItem('down', tokenActionIndex)"
            >
              <template #icon>
                <n-icon :component="ArrowDownIcon" />
              </template>
            </n-button>
            <n-button
              type="primary"
              secondary
              :title="$t('general.removeAction')"
              :disabled="model.tokens.length <= 1"
              :focusable="false"
              @click="() => removeTokenItem(tokenActionIndex)"
            >
              <template #icon>
                <n-icon :component="MinusIcon" />
              </template>
            </n-button>
            <n-button
              type="primary"
              secondary
              :title="$t('general.insertAction')"
              :disabled="model.tokens.length >= 1024"
              :focusable="false"
              @click="() => createTokenItem(tokenActionIndex)"
            >
              <template #icon>
                <n-icon :component="AddIcon" />
              </template>
            </n-button>
          </n-button-group>
        </template>
      </n-dynamic-input>
    </n-form-item>
  </template>
</template>
