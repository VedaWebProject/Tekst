<script setup lang="ts">
import type { AnyLayerUpdate, UserReadPublic } from '@/api';
import { layerFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { useAuthStore } from '@/stores';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import { h, type VNodeChild } from 'vue';
import UserDisplayText from '@/components/UserDisplayText.vue';
import {
  NCollapse,
  NCollapseItem,
  NSelect,
  NSpace,
  NIcon,
  NDynamicInput,
  NFormItem,
  NTag,
  NInput,
  NButton,
  type SelectOption,
} from 'naive-ui';

import MinusRound from '@vicons/material/MinusRound';
import AddOutlined from '@vicons/material/AddOutlined';
import PersonFilled from '@vicons/material/PersonFilled';
import type { SelectMixedOption } from 'naive-ui/es/select/src/interface';

const props = defineProps<{
  model: AnyLayerUpdate;
  categoryOptions: SelectMixedOption[];
  shareReadOptions: SelectMixedOption[];
  shareWriteOptions: SelectMixedOption[];
  loading?: boolean;
  loadingUsers?: boolean;
  errorUsers?: boolean;
  owner?: UserReadPublic | null;
  public?: boolean;
}>();

const emits = defineEmits(['update:model', 'search:users']);

const auth = useAuthStore();

function handleUpdate(field: string, value: any) {
  emits('update:model', {
    ...props.model,
    [field]: value,
  });
}

function renderUserSelectLabel(option: SelectOption): VNodeChild {
  return h(UserDisplayText, { user: option.user as UserReadPublic });
}

function renderUserSelectTag(props: { option: SelectOption; handleClose: () => void }): VNodeChild {
  return h(
    NTag,
    {
      closable: true,
      bordered: false,
      onMousedown: (e: FocusEvent) => {
        e.preventDefault();
      },
      onClose: (e: MouseEvent) => {
        e.stopPropagation();
        props.handleClose();
      },
    },
    {
      default: () => `@${(props.option.user as UserReadPublic).username}`,
      icon: () => h(NIcon, null, { default: () => h(PersonFilled) }),
    }
  );
}
</script>

<template>
  <n-collapse>
    <!-- TITLE -->
    <n-form-item path="title" :label="$t('models.layer.title')" required>
      <n-input
        :value="model.title"
        type="text"
        :placeholder="$t('models.layer.title')"
        :disabled="loading"
        @update:value="(v) => handleUpdate('title', v)"
        @keydown.enter.prevent
      />
    </n-form-item>
    <!-- DESCRIPTION -->
    <TranslationFormItem
      :value="model.description"
      parent-form-path-prefix="description"
      :loading="loading"
      :disabled="loading"
      :main-form-label="$t('models.layer.description')"
      :translation-form-label="$t('models.layer.description')"
      :translation-form-rule="layerFormRules.descriptionTranslation"
      @update:value="(v) => handleUpdate('description', v)"
    />
    <!-- CATEGORY -->
    <n-form-item :label="$t('models.layer.category')">
      <n-select
        :value="model.category"
        clearable
        :disabled="loading"
        :placeholder="$t('browse.uncategorized')"
        :options="categoryOptions"
        @update:value="(v) => handleUpdate('category', v)"
      />
    </n-form-item>
    <!-- CITATION -->
    <n-form-item path="citation" :label="$t('models.layer.citation')">
      <n-input
        :value="model.citation"
        type="text"
        :placeholder="$t('models.layer.citation')"
        :disabled="loading"
        @keydown.enter.prevent
        @update:value="(v) => handleUpdate('citation', v)"
      />
    </n-form-item>
    <!-- COMMENT -->
    <TranslationFormItem
      :value="model.comment"
      parent-form-path-prefix="comment"
      multiline
      :max-translation-length="2000"
      :disabled="loading"
      :main-form-label="$t('models.layer.comment')"
      :translation-form-label="$t('models.layer.comment')"
      :translation-form-rule="layerFormRules.commentTranslation"
      @update:value="(v) => handleUpdate('comment', v)"
    />
    <!-- METADATA -->
    <n-collapse-item :title="$t('models.meta.modelLabel')" name="meta">
      <n-form-item v-if="model.meta" :label="$t('models.meta.modelLabel')" :show-feedback="false">
        <n-dynamic-input
          :value="model.meta"
          item-style="margin-bottom: 0;"
          :min="0"
          :max="64"
          @create="() => ({ key: '', value: '' })"
          @update:value="(v) => handleUpdate('meta', v)"
        >
          <template #default="{ index, value: metaEntryValue }">
            <div style="display: flex; align-items: flex-start; gap: 12px; width: 100%">
              <n-form-item
                ignore-path-change
                :show-label="false"
                :path="`meta[${index}].key`"
                :rule="layerFormRules.metaKey"
                required
              >
                <n-input
                  v-model:value="metaEntryValue.key"
                  :placeholder="$t('models.meta.key')"
                  @keydown.enter.prevent
                />
              </n-form-item>
              <n-form-item
                ignore-path-changechange
                :show-label="false"
                :path="`meta[${index}].value`"
                :rule="layerFormRules.metaValue"
                style="flex-grow: 2"
                required
              >
                <n-input
                  v-model:value="metaEntryValue.value"
                  :placeholder="$t('models.meta.value')"
                  @keydown.enter.prevent
                />
              </n-form-item>
            </div>
          </template>
          <template #action="{ index: indexAction, create, remove }">
            <n-space style="margin-left: 20px; flex-wrap: nowrap">
              <n-button
                secondary
                circle
                :title="$t('general.removeAction')"
                @click="() => remove(indexAction)"
              >
                <template #icon>
                  <n-icon :component="MinusRound" />
                </template>
              </n-button>
              <n-button
                secondary
                circle
                :title="$t('general.insertAction')"
                :disabled="model.meta.length >= 64"
                @click="() => create(indexAction)"
              >
                <template #icon>
                  <n-icon :component="AddOutlined" />
                </template>
              </n-button>
            </n-space>
          </template>
        </n-dynamic-input>
      </n-form-item>
    </n-collapse-item>
    <!-- SHARES -->
    <n-collapse-item
      v-if="auth.user?.isSuperuser || (auth.user && owner && auth.user?.id === owner?.id)"
      :disabled="public"
      :title="
        $t('models.layer.share') + (public ? ` ${$t('dataLayers.edit.onlyForUnpublished')}` : '')
      "
      name="shares"
    >
      <n-form-item path="sharedRead" :label="$t('models.layer.sharedRead')">
        <n-select
          :value="model.sharedRead"
          multiple
          filterable
          clearable
          :render-label="renderUserSelectLabel"
          :render-tag="renderUserSelectTag"
          :loading="loadingUsers"
          :status="errorUsers ? 'error' : undefined"
          :placeholder="$t('models.layer.sharedRead')"
          :options="shareReadOptions"
          @update:value="(v) => handleUpdate('sharedRead', v)"
        />
      </n-form-item>
      <n-form-item path="sharedWrite" :label="$t('models.layer.sharedWrite')">
        <n-select
          :value="model.sharedWrite"
          multiple
          filterable
          clearable
          :render-label="renderUserSelectLabel"
          :render-tag="renderUserSelectTag"
          :loading="loadingUsers"
          :status="errorUsers ? 'error' : undefined"
          :placeholder="$t('models.layer.sharedWrite')"
          :options="shareWriteOptions"
          @update:value="(v) => handleUpdate('sharedWrite', v)"
        />
      </n-form-item>
    </n-collapse-item>
  </n-collapse>
</template>
