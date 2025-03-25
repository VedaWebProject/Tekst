<script setup lang="ts">
import { type AnyResourceRead, type PublicUserSearchFilters, type UserReadPublic } from '@/api';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import UserDisplayText from '@/components/user/UserDisplayText.vue';
import { usePublicUserSearch } from '@/composables/publicUserSearch';
import { $t } from '@/i18n';
import { UserIcon } from '@/icons';
import { useAuthStore } from '@/stores';
import { NAlert, NFormItem, NIcon, NSelect, NTag, type SelectOption } from 'naive-ui';
import { computed, h, ref, type VNodeChild } from 'vue';

const props = defineProps<{
  resource: AnyResourceRead;
}>();

const sharedRead = defineModel<string[]>('sharedRead', { required: true });
const sharedWrite = defineModel<string[]>('sharedWrite', { required: true });

const auth = useAuthStore();

const initialUserSearchQuery = (): PublicUserSearchFilters => ({
  pg: 1,
  pgs: 100,
  emptyOk: false,
});
const userSearchQuery = ref<PublicUserSearchFilters>(initialUserSearchQuery());

const {
  users: searchedUsers,
  loading: loadingUsers,
  error: errorUsers,
} = usePublicUserSearch(userSearchQuery);

const addedSharesUsersCache = ref<UserReadPublic[]>([]);

const sharingAuthorized = computed(
  () =>
    auth.user?.isSuperuser ||
    (auth.user && props.resource.owner && auth.user.id === props.resource.owner.id)
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
        props.resource.sharedReadUsers?.find((u) => u.id === id) ||
        props.resource.sharedWriteUsers?.find((u) => u.id === id) ||
        searchedUsers.value?.find((u) => u.id === id) ||
        addedSharesUsersCache.value.find((u) => u.id === id),
      disabled:
        id === props.resource.owner?.id ||
        (id === auth.user?.id && !auth.user?.isSuperuser) ||
        disabledIds.includes(id),
    }))
    .sort((a, b) => (a.disabled ? 1 : 0) - (b.disabled ? 1 : 0));
  return options;
}

const usersOptionsRead = computed(() => {
  return postprocessUserOptions(
    sharedRead.value,
    sharedWrite.value,
    searchedUsers.value.map((u) => u.id)
  );
});

const usersOptionsWrite = computed(() => {
  return postprocessUserOptions(
    sharedRead.value,
    sharedWrite.value,
    searchedUsers.value.map((u) => u.id)
  );
});

function onSharesUpdate(shares: string[]) {
  addedSharesUsersCache.value = [...addedSharesUsersCache.value, ...searchedUsers.value].filter(
    (u) =>
      sharedRead.value.includes(u.id) || sharedWrite.value.includes(u.id) || shares.includes(u.id)
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
  <div>
    <n-alert v-if="!sharingAuthorized" type="warning" :title="$t('common.warning')" class="mb-lg">
      {{ $t('resources.settings.sharingUnauthorized') }}
    </n-alert>
    <n-alert
      v-else-if="props.resource.public || props.resource.proposed"
      type="warning"
      :title="$t('common.important')"
      class="mb-lg"
    >
      {{ $t('resources.settings.unavailableWhenPublished') }}
    </n-alert>

    <form-section-heading v-if="sharingAuthorized" :label="$t('models.resource.sharedRead')" />

    <n-form-item v-if="sharingAuthorized" path="sharedRead" :show-label="false">
      <n-select
        v-model:value="sharedRead"
        multiple
        filterable
        clearable
        remote
        clear-filter-after-select
        :disabled="!sharingAuthorized || props.resource.public || props.resource.proposed"
        max-tag-count="responsive"
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

    <form-section-heading v-if="sharingAuthorized" :label="$t('models.resource.sharedWrite')" />

    <n-form-item v-if="sharingAuthorized" path="sharedWrite" :show-label="false">
      <n-select
        v-model:value="sharedWrite"
        multiple
        filterable
        clearable
        remote
        clear-filter-after-select
        :disabled="!sharingAuthorized || props.resource.public || props.resource.proposed"
        max-tag-count="responsive"
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
  </div>
</template>
