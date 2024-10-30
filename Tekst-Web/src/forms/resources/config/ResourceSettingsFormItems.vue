<script setup lang="ts">
import {
  prioritizedMetadataKeys,
  type AnyResourceConfig,
  type UserReadPublic,
  type AnyResourceRead,
  type PublicUserSearchFilters,
  type UserRead,
} from '@/api';
import { resourceSettingsFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { useAuthStore } from '@/stores';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import { computed, h, ref, type VNodeChild } from 'vue';
import UserDisplayText from '@/components/user/UserDisplayText.vue';
import CommonResourceConfigFormItems from '@/forms/resources/config/CommonResourceConfigFormItems.vue';
import SpecialResourceConfigFormItems from '@/forms/resources/config/SpecialResourceConfigFormItems.vue';
import { useUsersSearch } from '@/composables/fetchers';
import {
  NSelect,
  NIcon,
  NTabs,
  NTabPane,
  NDynamicInput,
  NFormItem,
  NTag,
  NInput,
  NFlex,
  type SelectOption,
} from 'naive-ui';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { UserIcon, TranslateIcon } from '@/icons';

const props = defineProps<{
  owner?: UserRead | UserReadPublic | null;
  public?: boolean;
}>();

const model = defineModel<AnyResourceRead>({ required: true });

const auth = useAuthStore();

const initialUserSearchQuery = (): PublicUserSearchFilters => ({
  pg: 1,
  pgs: 9999,
  emptyOk: false,
});
const userSearchQuery = ref<PublicUserSearchFilters>(initialUserSearchQuery());
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
        h(NIcon, { component: TranslateIcon }),
        $t(`models.meta.${k}`),
      ]),
    value: k,
    disabled: model.value.meta && !!model.value.meta.find((m) => m.key === k),
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
        model.value.sharedReadUsers?.find((u) => u.id === id) ||
        model.value.sharedWriteUsers?.find((u) => u.id === id) ||
        searchedUsers.value?.find((u) => u.id === id) ||
        addedSharesUsersCache.value.find((u) => u.id === id),
      disabled:
        id === model.value.ownerId ||
        (id === auth.user?.id && !auth.user?.isSuperuser) ||
        disabledIds.includes(id),
    }))
    .sort((a, b) => (a.disabled ? 1 : 0) - (b.disabled ? 1 : 0));
  return options;
}

const usersOptionsRead = computed(() => {
  return postprocessUserOptions(
    model.value.sharedRead,
    model.value.sharedWrite,
    searchedUsers.value.map((u) => u.id)
  );
});

const usersOptionsWrite = computed(() => {
  return postprocessUserOptions(
    model.value.sharedWrite,
    model.value.sharedRead,
    searchedUsers.value.map((u) => u.id)
  );
});

function handleUpdate(field: string, value: unknown) {
  model.value = {
    ...model.value,
    [field]: value,
  };
}

function handleSharesUpdate(field: string, value: string[]) {
  addedSharesUsersCache.value = [...addedSharesUsersCache.value, ...searchedUsers.value].filter(
    (u) =>
      model.value.sharedRead.includes(u.id) ||
      model.value.sharedWrite.includes(u.id) ||
      value.includes(u.id)
  );
  userSearchQuery.value = initialUserSearchQuery();
  handleUpdate(field, value);
}

function handleUserSearch(query: string) {
  userSearchQuery.value.q = query;
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
      icon: () => h(NIcon, null, { default: () => h(UserIcon) }),
    }
  );
}
</script>

<template>
  <n-tabs type="card" size="small" tab-style="font-size: var(--font-size-small)" pane-class="mt-md">
    <!-- GENERAL -->
    <n-tab-pane :tab="$t('general.general')" name="general">
      <!-- TITLE -->
      <translation-form-item
        :model-value="model.title"
        parent-form-path-prefix="title"
        :main-form-label="$t('models.resource.title')"
        :translation-form-label="$t('models.resource.title')"
        :translation-form-rule="resourceSettingsFormRules.titleTranslation"
        @update:model-value="(v) => handleUpdate('title', v)"
      />

      <!-- DESCRIPTION -->
      <translation-form-item
        :model-value="model.description"
        parent-form-path-prefix="description"
        :main-form-label="$t('models.resource.description')"
        :translation-form-label="$t('models.resource.description')"
        :translation-form-rule="resourceSettingsFormRules.descriptionTranslation"
        @update:model-value="(v) => handleUpdate('description', v)"
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
      <translation-form-item
        :model-value="model.comment"
        parent-form-path-prefix="comment"
        multiline
        :max-translation-length="2000"
        :main-form-label="$t('general.comment')"
        :translation-form-label="$t('general.comment')"
        :translation-form-rule="resourceSettingsFormRules.commentTranslation"
        @update:model-value="(v) => handleUpdate('comment', v)"
      />

      <!-- METADATA -->
      <n-form-item :label="$t('models.meta.modelLabel')" :show-feedback="false">
        <n-dynamic-input
          :value="model.meta"
          :min="0"
          :max="64"
          @create="() => ({ key: '', value: '' })"
          @update:value="(v) => handleUpdate('meta', v)"
        >
          <template #default="{ index, value: metaEntryValue }">
            <n-flex align="flex-start" wrap style="flex-grow: 2">
              <n-form-item
                ignore-path-change
                :show-label="false"
                :path="`meta[${index}].key`"
                :rule="resourceSettingsFormRules.metaKey"
                style="flex-grow: 1; min-width: 100px"
                required
              >
                <n-select
                  v-model:value="metaEntryValue.key"
                  filterable
                  tag
                  clearable
                  :options="metadataKeysOptions"
                />
              </n-form-item>
              <n-form-item
                ignore-path-changechange
                :show-label="false"
                :path="`meta[${index}].value`"
                :rule="resourceSettingsFormRules.metaValue"
                style="flex-grow: 2; min-width: 100px"
                required
              >
                <n-input
                  v-model:value="metaEntryValue.value"
                  :placeholder="$t('models.meta.value')"
                  @keydown.enter.prevent
                />
              </n-form-item>
            </n-flex>
          </template>
          <template #action="{ index: indexAction, create, remove, move }">
            <dynamic-input-controls
              :move-up-disabled="indexAction === 0"
              :move-down-disabled="indexAction === model.meta.length - 1"
              :insert-disabled="model.meta.length >= 64"
              @move-up="() => move('up', indexAction)"
              @move-down="() => move('down', indexAction)"
              @remove="() => remove(indexAction)"
              @insert="() => create(indexAction)"
            />
          </template>
        </n-dynamic-input>
      </n-form-item>
    </n-tab-pane>

    <!-- RESOURCE COMMON CONFIG -->
    <n-tab-pane :tab="$t('resources.settings.config.heading')" name="configCommon">
      <common-resource-config-form-items
        :model-value="model.config.common"
        @update:model-value="(u: any) => (model = { ...model, common: u })"
      />
    </n-tab-pane>

    <!-- RESOURCE SPECIAL CONFIG -->
    <n-tab-pane
      :tab="$t('resources.types.' + model.resourceType + '.label')"
      name="configTypeSpecific"
    >
      <!-- RESOURCE COMMON CONFIG -->
      <special-resource-config-form-items
        :model-value="model.config"
        :resource-type="model.resourceType"
        @update:model-value="(v: AnyResourceConfig) => handleUpdate('config', v)"
      />
    </n-tab-pane>

    <!-- ACCESS SHARES -->
    <n-tab-pane v-if="sharingAuthorized" :tab="$t('models.resource.share')" name="access">
      <div v-if="public" class="text-tiny mb-md" style="color: var(--col-error)">
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
    </n-tab-pane>
  </n-tabs>
</template>
