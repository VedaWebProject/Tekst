<script setup lang="ts">
import {
  prioritizedMetadataKeys,
  type AnyResourceConfig,
  type AnyResourceUpdate,
  type UserReadPublic,
} from '@/api';
import { resourceFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { useAuthStore, useStateStore } from '@/stores';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import { computed, h, ref, type VNodeChild } from 'vue';
import UserDisplayText from '@/components/UserDisplayText.vue';
import ResourceConfigFormItems from '@/forms/resources/config/ResourceConfigFormItems.vue';
import { usePlatformData } from '@/platformData';
import { pickTranslation } from '@/utils';
import { useUsersPublic } from '@/fetchers';
import {
  NSelect,
  NSpace,
  NIcon,
  NInputNumber,
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
import TranslateOutlined from '@vicons/material/TranslateOutlined';
import HelpButtonWidget from '@/components/widgets/HelpButtonWidget.vue';

const props = defineProps<{
  model: AnyResourceUpdate;
  owner?: UserReadPublic | null;
  public?: boolean;
}>();

const emits = defineEmits(['update:model']);

const state = useStateStore();
const auth = useAuthStore();
const { pfData } = usePlatformData();

const userSearchQuery = ref<string>();
const { users, loading: loadingUsers, error: errorUsers } = useUsersPublic(userSearchQuery);
const sharingAuthorized = computed(
  () => auth.user?.isSuperuser || (auth.user && props.owner && auth.user.id === props.owner.id)
);

const categoryOptions = computed(
  () =>
    pfData.value?.settings.resourceCategories?.map((c) => ({
      label: pickTranslation(c.translations, state.locale) || c.key,
      value: c.key,
    })) || []
);

const metadataKeysOptions = computed(() =>
  prioritizedMetadataKeys.map((k) => ({
    label: () =>
      h('div', { style: 'display: flex; align-items: center; gap: 4px; padding: 4px' }, [
        h(NIcon, { component: TranslateOutlined }),
        $t(`models.meta.${k}`),
      ]),
    value: k,
    disabled: props.model.meta && !!props.model.meta.find((m) => m.key === k),
  }))
);

const usersOptions = computed(() =>
  users.value.map((u) => {
    return {
      value: u.id,
      disabled:
        u.id === auth.user?.id ||
        !!props.model.sharedRead?.find((s) => s === u.id) ||
        !!props.model.sharedWrite?.find((s) => s === u.id),
      user: u,
    };
  })
);

function handleUpdate(field: string, value: any) {
  emits('update:model', {
    ...props.model,
    [field]: value,
  });
}

function handleUserSearch(query: string) {
  userSearchQuery.value = query;
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
  <div class="content-block">
    <h3>{{ $t('resources.headingGeneral') }}</h3>
    <!-- TITLE -->
    <n-form-item path="title" :label="$t('models.resource.title')" required>
      <n-input
        :value="model.title"
        type="text"
        :placeholder="$t('models.resource.title')"
        @update:value="(v) => handleUpdate('title', v)"
        @keydown.enter.prevent
      />
    </n-form-item>
    <!-- DESCRIPTION -->
    <TranslationFormItem
      :value="model.description"
      parent-form-path-prefix="description"
      :main-form-label="$t('models.resource.description')"
      :translation-form-label="$t('models.resource.description')"
      :translation-form-rule="resourceFormRules.descriptionTranslation"
      @update:value="(v) => handleUpdate('description', v)"
    />
    <!-- CITATION -->
    <n-form-item path="citation" :label="$t('models.resource.citation')">
      <n-input
        :value="model.citation"
        type="text"
        :placeholder="$t('models.resource.citation')"
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
      :main-form-label="$t('models.resource.comment')"
      :translation-form-label="$t('models.resource.comment')"
      :translation-form-rule="resourceFormRules.commentTranslation"
      @update:value="(v) => handleUpdate('comment', v)"
    />
    <!-- CATEGORY -->
    <n-form-item :label="$t('models.resource.category')">
      <n-select
        :value="model.category"
        clearable
        :placeholder="$t('browse.uncategorized')"
        :options="categoryOptions"
        @update:value="(v) => handleUpdate('category', v)"
      />
    </n-form-item>
    <!-- SORT ORDER -->
    <n-form-item path="sortOrder" :label="$t('models.resource.sortOrder')">
      <n-input-number
        :min="0"
        :value="model.sortOrder"
        style="width: 100%"
        @update:value="(v) => handleUpdate('sortOrder', v)"
      />
    </n-form-item>
  </div>

  <!-- METADATA -->
  <div class="content-block">
    <h3>
      {{ $t('models.meta.modelLabel') }}
      <HelpButtonWidget help-key="metadataForm" />
    </h3>
    <n-form-item v-if="model.meta" :show-label="false" :show-feedback="false">
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
              :rule="resourceFormRules.metaKey"
              required
            >
              <n-select
                v-model:value="metaEntryValue.key"
                filterable
                tag
                :options="metadataKeysOptions"
              />
            </n-form-item>
            <n-form-item
              ignore-path-changechange
              :show-label="false"
              :path="`meta[${index}].value`"
              :rule="resourceFormRules.metaValue"
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
  </div>

  <!-- CONFIG -->
  <div v-if="model.config" class="content-block">
    <ResourceConfigFormItems
      :model="model.config"
      :resource-type="model.resourceType"
      @update:model="(v: AnyResourceConfig) => handleUpdate('config', v)"
    />
  </div>

  <!-- ACCESS SHARES -->
  <div v-if="sharingAuthorized && model.sharedRead && model.sharedWrite" class="content-block">
    <h3>{{ $t('models.resource.share') }}</h3>
    <div
      v-if="public"
      style="
        font-size: var(--app-ui-font-size-tiny);
        color: var(--col-error);
        margin-bottom: var(--content-gap);
      "
    >
      {{ $t('resources.edit.onlyForUnpublished') }}
    </div>
    <n-form-item path="sharedRead" :label="$t('models.resource.sharedRead')">
      <n-select
        :value="model.sharedRead"
        multiple
        filterable
        clearable
        remote
        clear-filter-after-select
        :disabled="!sharingAuthorized || public"
        :max-tag-count="64"
        :render-label="renderUserSelectLabel"
        :render-tag="renderUserSelectTag"
        :loading="loadingUsers"
        :status="errorUsers ? 'error' : undefined"
        :options="usersOptions"
        :placeholder="$t('resources.phSearchUsers')"
        @update:value="(v) => handleUpdate('sharedRead', v)"
        @search="handleUserSearch"
      />
    </n-form-item>
    <n-form-item path="sharedWrite" :label="$t('models.resource.sharedWrite')">
      <n-select
        :value="model.sharedWrite"
        multiple
        filterable
        clearable
        remote
        clear-filter-after-select
        :disabled="!sharingAuthorized || public"
        :max-tag-count="64"
        :render-label="renderUserSelectLabel"
        :render-tag="renderUserSelectTag"
        :loading="loadingUsers"
        :status="errorUsers ? 'error' : undefined"
        :options="usersOptions"
        :placeholder="$t('resources.phSearchUsers')"
        @update:value="(v) => handleUpdate('sharedWrite', v)"
        @search="handleUserSearch"
      />
    </n-form-item>
  </div>
</template>
