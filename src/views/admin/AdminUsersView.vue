<script setup lang="ts">
import { useUsers } from '@/fetchers';
import type { DataTableColumn, PaginationProps } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import { NDataTable, NIcon, NModal, NCheckbox } from 'naive-ui';
import { UsersApi, type UserRead, type UserUpdate } from '@/openapi';
import { ref, h, type Component } from 'vue';
import { configureApi } from '@/openApiConfig';
import { useMessagesStore } from '@/stores';

import CheckRound from '@vicons/material/CheckRound';
import ShieldTwotone from '@vicons/material/ShieldTwotone';
import ManageAccountsRound from '@vicons/material/ManageAccountsRound';

const { users, error, load: loadUsers } = useUsers();
const { t } = useI18n({ useScope: 'global' });

// icons
const iconElement = (icon: Component) => h(NIcon, null, { default: () => h(icon) });
const iconCheck = iconElement(CheckRound);
const iconSuperuser = iconElement(ShieldTwotone);
const iconEditUser = iconElement(ManageAccountsRound);

// things related to updating users
interface UserUpdatePayload {
  id?: string;
  username?: string;
  updates: UserUpdate;
}
const usersApi = configureApi(UsersApi);
const messages = useMessagesStore();
const showUserUpdateModal = ref(false);
const initialUserUpdates: UserUpdatePayload = { updates: {} };
const userUpdates = ref<UserUpdatePayload>(initialUserUpdates);
const handleOpenUserUpdate = (user: UserRead) => {
  userUpdates.value = {
    id: user.id,
    username: user.username,
    // selectively add user properties to possible updates
    updates: {
      isActive: user.isActive,
      isVerified: user.isVerified,
      isSuperuser: user.isSuperuser,
    },
  };
  showUserUpdateModal.value = true;
};
const handleCloseUserUpdate = () => {
  userUpdates.value = initialUserUpdates;
  showUserUpdateModal.value = false;
};
const handleSaveUserUpdate = async () => {
  try {
    if (!userUpdates.value.id || !userUpdates.value.updates) {
      throw new Error();
    }
    await usersApi.usersPatchUser({
      id: userUpdates.value.id,
      userUpdate: userUpdates.value.updates,
    });
    messages.success(t('admin.users.save', { username: userUpdates.value.username }));
  } catch {
    messages.error(t('errors.unexpected'));
  } finally {
    loadUsers();
    handleCloseUserUpdate();
  }
};

const columns: Array<DataTableColumn> = [
  {
    key: 'email',
    title: t('user.fields.email'),
    sorter: 'default',
  },
  {
    key: 'username',
    title: t('user.fields.username'),
    defaultSortOrder: 'ascend',
    sorter: 'default',
  },
  {
    key: 'firstName',
    title: t('user.fields.firstName'),
    sorter: 'default',
  },
  {
    key: 'lastName',
    title: t('user.fields.lastName'),
    sorter: 'default',
  },
  {
    key: 'affiliation',
    title: t('user.fields.affiliation'),
    sorter: 'default',
  },
  {
    key: 'isActive',
    title: t('user.fields.active'),
    render: (u) => (u.isActive ? iconCheck : null),
    align: 'center',
    // @ts-ignore
    sorter: (r1, r2) => r2.isActive - r1.isActive,
  },
  {
    key: 'isVerified',
    title: t('user.fields.verified'),
    render: (u) => (u.isVerified ? iconCheck : null),
    align: 'center',
    // @ts-ignore
    sorter: (r1, r2) => r2.isVerified - r1.isVerified,
  },
  {
    key: 'isSuperuser',
    title: t('user.fields.superuser'),
    render: (u) => (u.isSuperuser ? iconSuperuser : null),
    align: 'center',
    // @ts-ignore
    sorter: (r1, r2) => r2.isSuperuser - r1.isSuperuser,
  },
];

const pagination: PaginationProps = {
  pageSizes: [10, 20, 50, 100],
  pageSize: 10,
};

function rowClassName(user: UserRead) {
  if (!user.isActive) return 'inactive';
  if (!user.isVerified) return 'unverified';
  if (user.isSuperuser) return 'superuser';
  return '';
}

function rowProps(user: UserRead) {
  return {
    style: 'cursor: pointer;',
    onClick: () => handleOpenUserUpdate(user),
  };
}
</script>

<template>
  <h1>{{ $t('admin.heading') }}: {{ $t('admin.users.heading') }}</h1>

  <div v-if="!error" class="content-block">
    <n-data-table
      pagination-behavior-on-filter="first"
      :columns="columns"
      :data="users || []"
      :loading="!users"
      :row-key="(rowData) => rowData.id"
      :pagination="pagination"
      :row-class-name="rowClassName"
      :row-props="rowProps"
      size="small"
    />
  </div>

  <div v-else>
    {{ $t('errors.error') }}
  </div>

  <n-modal
    v-model:show="showUserUpdateModal"
    preset="dialog"
    :title="`${t('internals.user')}: ${userUpdates?.username}`"
    :icon="() => iconEditUser"
    positive-text="Save"
    negative-text="Cancel"
    @positive-click="handleSaveUserUpdate"
    @negative-click="handleCloseUserUpdate"
  >
    <n-checkbox v-model:checked="userUpdates.updates.isActive">active</n-checkbox>
    <n-checkbox v-model:checked="userUpdates.updates.isVerified">verified</n-checkbox>
    <n-checkbox v-model:checked="userUpdates.updates.isSuperuser">Superuser</n-checkbox>
  </n-modal>
</template>

<style scoped>
:deep(.n-data-table .n-data-table-td) {
  background-color: unset !important;
}

:deep(.inactive td:first-child) {
  border-left: 4px solid rgba(255, 0, 0, 0.75);
}
:deep(.inactive td:first-child) {
  border-left: 4px solid rgba(255, 0, 0, 0.75);
}

:deep(.inactive) {
  background-color: rgba(255, 0, 0, 0.1);
}

:deep(.unverified td:first-child) {
  border-left: 4px solid rgba(255, 145, 0, 0.75);
}

:deep(.unverified) {
  background-color: rgba(255, 145, 0, 0.1);
}

:deep(.superuser td:first-child) {
  border-left: 4px solid rgba(0, 60, 255, 0.75);
}

:deep(.superuser) {
  background-color: rgba(0, 60, 255, 0.1);
}
</style>
