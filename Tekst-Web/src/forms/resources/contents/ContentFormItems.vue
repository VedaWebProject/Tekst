<script setup lang="ts">
import type { AnyContentCreate, AnyResourceRead } from '@/api';
import { dynInputCreateBtnProps } from '@/common';
import FormSection from '@/components/FormSection.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { contentFormRules } from '@/forms/formRules';
import resourceContentFormItems from '@/forms/resources/contents/mappings';
import {
  NBadge,
  NCollapse,
  NCollapseItem,
  NDynamicInput,
  NFlex,
  NFormItem,
  NInput,
} from 'naive-ui';

const props = defineProps<{
  resource: AnyResourceRead;
}>();

const model = defineModel<AnyContentCreate>({ required: true });

const contentFontStyle = {
  fontFamily: props.resource.config.general.font || 'var(--font-family-content)',
};
</script>

<template>
  <form-section v-if="model" :title="$t('common.content')">
    <!-- CONTENT -->
    <component
      :is="resourceContentFormItems[model.resourceType]"
      v-model="model"
      :resource="resource"
    />

    <!-- CONTENT METADATA FIELDS -->
    <n-collapse :default-expanded-names="['comments']" class="mt-md">
      <n-collapse-item name="comments">
        <template #header>
          <n-badge dot :show="!!model.authorsComment || !!model.editorsComments" :offset="[6, 10]">
            <b class="text-medium">{{ $t('common.comment', 2) }}</b>
          </n-badge>
        </template>
        <!-- AUTHORS COMMENT -->
        <n-form-item
          :label="$t('resources.types.common.contentFields.authorsComment')"
          path="authorsComment"
          :rule="contentFormRules.common.authorsComment"
        >
          <n-input
            v-model:value="model.authorsComment"
            type="textarea"
            :rows="3"
            :maxlength="50000"
            show-count
            :placeholder="$t('common.comment')"
            :style="contentFontStyle"
          />
        </n-form-item>

        <!-- EDITORS COMMENT -->
        <n-form-item
          :label="$t('resources.types.common.contentFields.editorsComments')"
          path="editorsComments"
          class="parent-form-item"
        >
          <n-dynamic-input
            v-model:value="model.editorsComments"
            :min="1"
            :max="100"
            :create-button-props="dynInputCreateBtnProps"
            item-class="divided"
            @create="() => ({ by: '', comment: '' })"
          >
            <template #default="{ index, value }">
              <n-flex align="flex-start" style="flex: 2">
                <n-form-item
                  ignore-path-change
                  :label="$t('common.name')"
                  :path="`editorsComments[${index}].by`"
                  :rule="contentFormRules.common.editorsCommentBy"
                  style="flex: 2 200px"
                >
                  <n-input v-model:value="value.by" :placeholder="$t('common.name')" />
                </n-form-item>
                <n-form-item
                  ignore-path-change
                  :label="$t('common.comment')"
                  :path="`editorsComments[${index}].comment`"
                  :rule="contentFormRules.common.editorsComment"
                  style="flex: 3 320px"
                >
                  <n-input
                    v-model:value="value.comment"
                    type="textarea"
                    :rows="3"
                    :maxlength="5000"
                    show-count
                    :placeholder="$t('common.comment')"
                    :style="contentFontStyle"
                    style="flex: 3"
                  />
                </n-form-item>
              </n-flex>
            </template>
            <template #action="{ index, create, remove, move }">
              <dynamic-input-controls
                top-offset
                movable
                :insert-disabled="(model.editorsComments?.length || 0) >= 64"
                :remove-disabled="(model.editorsComments?.length || 0) <= 1"
                :move-up-disabled="index === 0"
                :move-down-disabled="index === (model.editorsComments?.length || 0) - 1"
                @remove="() => remove(index)"
                @insert="() => create(index)"
                @move-up="move('up', index)"
                @move-down="move('down', index)"
              />
            </template>
          </n-dynamic-input>
        </n-form-item>
      </n-collapse-item>
    </n-collapse>
  </form-section>
</template>
