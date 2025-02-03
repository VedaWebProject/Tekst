<script setup lang="ts">
import {
  type AnyResourceConfig,
  type AnyResourceRead,
  type PublicUserSearchFilters,
  type UserRead,
  type UserReadPublic,
} from '@/api';
import UserDisplayText from '@/components/user/UserDisplayText.vue';
import { useUsersSearch } from '@/composables/fetchers';
import CommonResourceConfigFormItems from '@/forms/resources/config/CommonResourceConfigFormItems.vue';
import ResourceSettingsGeneralFormItems from '@/forms/resources/config/ResourceSettingsGeneralFormItems.vue';
import SpecialResourceConfigFormItems from '@/forms/resources/config/SpecialResourceConfigFormItems.vue';
import { $t } from '@/i18n';
import { UserIcon } from '@/icons';
import { useAuthStore } from '@/stores';
import {
  NFormItem,
  NIcon,
  NSelect,
  NTabPane,
  NTabs,
  NTag,
  useThemeVars,
  type SelectOption,
} from 'naive-ui';
import { computed, h, ref, type VNodeChild } from 'vue';

const props = defineProps<{
  owner?: UserRead | UserReadPublic | null;
  public?: boolean;
  proposed?: boolean;
}>();

const model = defineModel<AnyResourceRead>({ required: true });

const auth = useAuthStore();
const nuiTheme = useThemeVars();

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

function onSharesUpdate(shares: string[]) {
  addedSharesUsersCache.value = [...addedSharesUsersCache.value, ...searchedUsers.value].filter(
    (u) =>
      model.value.sharedRead.includes(u.id) ||
      model.value.sharedWrite.includes(u.id) ||
      shares.includes(u.id)
  );
  userSearchQuery.value = initialUserSearchQuery();
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
      <resource-settings-general-form-items
        :model-value="model"
        @update:model-value="
          (v: AnyResourceRead) => {
            model = v;
          }
        "
      />
    </n-tab-pane>

    <!-- RESOURCE COMMON CONFIG -->
    <n-tab-pane :tab="$t('resources.settings.config.heading')" name="configCommon">
      <common-resource-config-form-items
        :model-value="model.config.common"
        :resource-type="model.resourceType"
        @update:model-value="
          (u: AnyResourceConfig['common']) => {
            model.config.common = u;
          }
        "
      />
    </n-tab-pane>

    <!-- RESOURCE SPECIAL CONFIG -->
    <n-tab-pane
      :tab="$t('resources.types.' + model.resourceType + '.label')"
      name="configTypeSpecific"
    >
      <!-- RESOURCE COMMON CONFIG -->
      <special-resource-config-form-items
        v-model="model.config"
        :resource-type="model.resourceType"
      />
    </n-tab-pane>

    <!-- ACCESS SHARES -->
    <n-tab-pane v-if="sharingAuthorized" :tab="$t('models.resource.share')" name="access">
      <div
        v-if="public || proposed"
        class="text-tiny mb-md"
        :style="{ color: nuiTheme.errorColor }"
      >
        {{ $t('resources.settings.onlyForPrivate') }}
      </div>
      <n-form-item path="sharedRead" :label="$t('models.resource.sharedRead')">
        <n-select
          v-model:value="model.sharedRead"
          multiple
          filterable
          clearable
          remote
          clear-filter-after-select
          :disabled="!sharingAuthorized || public || proposed"
          :max-tag-count="64"
          :render-label="renderUserSelectLabel"
          :render-tag="renderUserSelectTag"
          :loading="loadingUsers"
          :status="errorUsers ? 'error' : undefined"
          :options="usersOptionsRead"
          :placeholder="$t('resources.phSearchUsers')"
          @update:value="(v) => onSharesUpdate(v)"
          @search="handleUserSearch"
        />
      </n-form-item>
      <n-form-item path="sharedWrite" :label="$t('models.resource.sharedWrite')">
        <n-select
          v-model:value="model.sharedWrite"
          multiple
          filterable
          clearable
          remote
          clear-filter-after-select
          :disabled="!sharingAuthorized || public || proposed"
          :max-tag-count="64"
          :render-label="renderUserSelectLabel"
          :render-tag="renderUserSelectTag"
          :loading="loadingUsers"
          :status="errorUsers ? 'error' : undefined"
          :options="usersOptionsWrite"
          :placeholder="$t('resources.phSearchUsers')"
          @update:value="(v) => onSharesUpdate(v)"
          @search="handleUserSearch"
        />
      </n-form-item>
    </n-tab-pane>
  </n-tabs>
</template>
