<script setup lang="ts">
import { useUsers } from '@/fetchers';
import type { DataTableColumn, PaginationProps } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import { NDataTable, NIcon } from 'naive-ui';
import type { UserRead } from '@/openapi';
import { h, type Component } from 'vue';

import CheckRound from '@vicons/material/CheckRound';
import ShieldTwotone from '@vicons/material/ShieldTwotone';

const { users, error } = useUsers();
const { t } = useI18n({ useScope: 'global' });

const iconElement = (icon: Component) => h(NIcon, null, { default: () => h(icon) });
const iconCheck = iconElement(CheckRound);
const iconSuperuser = iconElement(ShieldTwotone);

const columns: Array<DataTableColumn> = [
  {
    key: 'email',
    title: t('user.fields.email'),
  },
  {
    key: 'username',
    title: t('user.fields.username'),
  },
  {
    key: 'firstName',
    title: t('user.fields.firstName'),
  },
  {
    key: 'lastName',
    title: t('user.fields.lastName'),
  },
  {
    key: 'affiliation',
    title: t('user.fields.affiliation'),
  },
  {
    key: 'isActive',
    title: t('user.fields.active'),
    render: (u) => (u.isActive ? iconCheck : null),
    align: 'center',
  },
  {
    key: 'isVerified',
    title: t('user.fields.verified'),
    render: (u) => (u.isVerified ? iconCheck : null),
    align: 'center',
  },
  {
    key: 'isSuperuser',
    title: t('user.fields.superuser'),
    render: (u) => (u.isSuperuser ? iconSuperuser : null),
    align: 'center',
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
</script>

<template>
  <h1>{{ $t('admin.heading') }}: {{ $t('admin.users.heading') }}</h1>

  <div v-if="!error" style="margin-top: 1rem">
    <n-data-table
      pagination-behavior-on-filter="first"
      :columns="columns"
      :data="users || []"
      :loading="!users"
      :row-key="(rowData) => rowData.id"
      :pagination="pagination"
      :row-class-name="rowClassName"
    />
  </div>

  <div v-else>
    {{ $t('errors.error') }}
  </div>
</template>

<style scoped>
:deep(.n-data-table .n-data-table-td) {
  background-color: unset !important;
}
:deep(.inactive td:first-child) {
  border-left: 4px solid rgba(255, 0, 0, 0.75);
}

:deep(.inactive) {
  background-color: rgba(255, 0, 0, 0.05);
}

:deep(.unverified td:first-child) {
  border-left: 4px solid rgba(255, 145, 0, 0.75);
}

:deep(.unverified) {
  background-color: rgba(255, 145, 0, 0.05);
}

:deep(.superuser td:first-child) {
  border-left: 4px solid rgba(0, 60, 255, 0.75);
}

:deep(.superuser) {
  background-color: rgba(0, 60, 255, 0.05);
}
</style>
