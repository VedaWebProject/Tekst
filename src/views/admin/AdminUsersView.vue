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
import ClearRound from '@vicons/material/ClearRound';
import ShieldTwotone from '@vicons/material/ShieldTwotone';
import ManageAccountsRound from '@vicons/material/ManageAccountsRound';

const { users, error, load: loadUsers } = useUsers();
const { t } = useI18n({ useScope: 'global' });

// icons
const iconElement = (icon: Component, color?: string) =>
  h(NIcon, { color }, { default: () => h(icon) });
const iconCheck = iconElement(CheckRound, 'var(--col-success)');
const iconCross = iconElement(ClearRound, 'var(--col-error)');
const iconSuperuser = iconElement(ShieldTwotone, 'var(--col-info)');
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
const emptyUserUpdatePayload: UserUpdatePayload = { updates: {} };
const userUpdatesPayload = ref<UserUpdatePayload>(emptyUserUpdatePayload);
const handleOpenUserUpdate = (user: UserRead) => {
  userUpdatesPayload.value = {
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
  userUpdatesPayload.value = emptyUserUpdatePayload;
  showUserUpdateModal.value = false;
};
const handleSaveUserUpdate = async () => {
  try {
    if (!userUpdatesPayload.value.id || !userUpdatesPayload.value.updates) {
      throw new Error();
    }
    await usersApi.usersPatchUser({
      id: userUpdatesPayload.value.id,
      userUpdate: userUpdatesPayload.value.updates,
    });
    messages.success(t('admin.users.save', { username: userUpdatesPayload.value.username }));
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
    render: (u) => (u.isActive ? iconCheck : iconCross),
    align: 'center',
    // @ts-ignore
    sorter: (r1, r2) => r2.isActive - r1.isActive,
  },
  {
    key: 'isVerified',
    title: t('user.fields.verified'),
    render: (u) => (u.isVerified ? iconCheck : iconCross),
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
  defaultPageSize: 10,
  showSizePicker: true,
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

  <div v-if="!error">
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
    to="#app-container"
    :title="`${t('internals.user')}: ${userUpdatesPayload?.username || ''}`"
    :icon="() => iconEditUser"
    :positive-text="$t('general.saveAction')"
    :negative-text="$t('general.cancelAction')"
    @positive-click="handleSaveUserUpdate"
    @negative-click="handleCloseUserUpdate"
  >
    <div style="display: flex; flex-direction: column; gap: 4px; margin: 24px 0">
      <n-checkbox v-model:checked="userUpdatesPayload.updates.isActive">
        {{ $t('admin.users.checkLabelActive') }}
      </n-checkbox>
      <n-checkbox v-model:checked="userUpdatesPayload.updates.isVerified">
        {{ $t('admin.users.checkLabelVerified') }}
      </n-checkbox>
      <div
        style="
          padding: 8px 4px 0px 0px;
          font-size: var(--app-ui-font-size-tiny);
          font-weight: var(--app-ui-font-weight-light);
          color: var(--col-error) !important;
        "
      >
        {{ $t('admin.users.editModal.adminWarning') }}
      </div>
      <n-checkbox v-model:checked="userUpdatesPayload.updates.isSuperuser">
        {{ $t('admin.users.checkLabelSuperuser') }}
      </n-checkbox>
    </div>
  </n-modal>
</template>

<style scoped></style>
