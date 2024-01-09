<script setup lang="ts">
import {
  prioritizedMetadataKeys,
  type AnyResourceConfig,
  type UserReadPublic,
  type AnyResourceRead,
} from '@/api';
import { resourceConfigFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { useAuthStore } from '@/stores';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import { computed, h, ref, type VNodeChild } from 'vue';
import UserDisplayText from '@/components/UserDisplayText.vue';
import ResourceConfigFormItems from '@/forms/resources/config/ResourceConfigFormItems.vue';
import { useUsersSearch } from '@/fetchers';
import HelpButtonWidget from '@/components/widgets/HelpButtonWidget.vue';
import {
  NSelect,
  NSpace,
  NIcon,
  NDivider,
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
import ArrowUpwardOutlined from '@vicons/material/ArrowUpwardOutlined';
import ArrowDownwardOutlined from '@vicons/material/ArrowDownwardOutlined';

const props = defineProps<{
  model: AnyResourceRead;
  owner?: UserReadPublic | null;
  public?: boolean;
}>();

const emits = defineEmits(['update:model']);

const auth = useAuthStore();

const userSearchQuery = ref<string>();
const {
  users: searchedUsers,
  loading: loadingUsers,
  error: errorUsers,
} = useUsersSearch(userSearchQuery);
const addedSharesUsersCache = ref<UserReadPublic[]>([]);
const sharingAuthorized = computed(
  () => auth.user?.isSuperuser || (auth.user && props.owner && auth.user.id === props.owner.id)
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

function postprocessUserOptions(
  sharedIds: string[] = [],
  disabledIds: string[] = [],
  searchResultsIds: string[] = []
) {
  const options = [...new Set([...sharedIds, ...disabledIds, ...searchResultsIds])]
    .map((id) => ({
      value: id,
      user:
        props.model.sharedReadUsers?.find((u) => u.id === id) ||
        props.model.sharedWriteUsers?.find((u) => u.id === id) ||
        searchedUsers.value?.find((u) => u.id === id) ||
        addedSharesUsersCache.value.find((u) => u.id === id),
      disabled:
        id === props.model.ownerId ||
        (id === auth.user?.id && !auth.user?.isSuperuser) ||
        disabledIds.includes(id),
    }))
    .sort((a, b) => (a.disabled ? 1 : 0) - (b.disabled ? 1 : 0));
  return options;
}

const usersOptionsRead = computed(() => {
  return postprocessUserOptions(
    props.model.sharedRead,
    props.model.sharedWrite,
    searchedUsers.value.map((u) => u.id)
  );
});

const usersOptionsWrite = computed(() => {
  return postprocessUserOptions(
    props.model.sharedWrite,
    props.model.sharedRead,
    searchedUsers.value.map((u) => u.id)
  );
});

function handleUpdate(field: string, value: any) {
  emits('update:model', {
    ...props.model,
    [field]: value,
  });
}

function handleSharesUpdate(field: string, value: string[]) {
  addedSharesUsersCache.value = [...addedSharesUsersCache.value, ...searchedUsers.value].filter(
    (u) =>
      props.model.sharedRead?.includes(u.id) ||
      props.model.sharedWrite?.includes(u.id) ||
      value.includes(u.id)
  );
  handleUpdate(field, value);
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
    :translation-form-rule="resourceConfigFormRules.descriptionTranslation"
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
    :translation-form-rule="resourceConfigFormRules.commentTranslation"
    @update:value="(v) => handleUpdate('comment', v)"
  />

  <n-divider />

  <!-- METADATA -->
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
            :rule="resourceConfigFormRules.metaKey"
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
            :rule="resourceConfigFormRules.metaValue"
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
      <template #action="{ index: indexAction, create, remove, move }">
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
          <n-button
            secondary
            circle
            :title="$t('general.moveUpAction')"
            :disabled="indexAction === 0"
            :focusable="false"
            @click="() => move('up', indexAction)"
          >
            <template #icon>
              <n-icon :component="ArrowUpwardOutlined" />
            </template>
          </n-button>
          <n-button
            secondary
            circle
            :title="$t('general.moveDownAction')"
            :disabled="indexAction === model.meta.length - 1"
            :focusable="false"
            @click="() => move('down', indexAction)"
          >
            <template #icon>
              <n-icon :component="ArrowDownwardOutlined" />
            </template>
          </n-button>
        </n-space>
      </template>
    </n-dynamic-input>
  </n-form-item>

  <n-divider />

  <!-- CONFIG -->
  <template v-if="model.config">
    <ResourceConfigFormItems
      :model="model.config"
      :resource-type="model.resourceType"
      @update:model="(v: AnyResourceConfig) => handleUpdate('config', v)"
    />
  </template>

  <n-divider />

  <!-- ACCESS SHARES -->
  <template v-if="sharingAuthorized && model.sharedRead && model.sharedWrite">
    <h3>{{ $t('models.resource.share') }}</h3>
    <div
      v-if="public"
      style="
        font-size: var(--app-ui-font-size-tiny);
        color: var(--col-error);
        margin-bottom: var(--content-gap);
      "
    >
      {{ $t('resources.settings.onlyForUnpublished') }}
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
        :options="usersOptionsRead"
        :placeholder="$t('resources.phSearchUsers')"
        @update:value="(v) => handleSharesUpdate('sharedRead', v)"
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
        :options="usersOptionsWrite"
        :placeholder="$t('resources.phSearchUsers')"
        @update:value="(v) => handleSharesUpdate('sharedWrite', v)"
        @search="handleUserSearch"
      />
    </n-form-item>
  </template>
</template>
