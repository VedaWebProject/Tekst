<script setup lang="ts">
import { onMounted } from 'vue';
import { useUsersAdmin } from '@/fetchers';
import {
  NButton,
  NInput,
  NIcon,
  NCheckbox,
  NSpace,
  NSpin,
  NPagination,
  NList,
  NCollapse,
  NCollapseItem,
  useDialog,
} from 'naive-ui';
import UserListItem from '@/components/admin/UserListItem.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import type { UserRead, UserUpdate } from '@/api';
import { ref } from 'vue';
import { computed } from 'vue';
import { useMessages } from '@/messages';
import { $t } from '@/i18n';
import { useRoute } from 'vue-router';
import { POST, PATCH, DELETE } from '@/api';
import { useAuthStore } from '@/stores';
import { positiveButtonProps, negativeButtonProps } from '@/components/dialogButtonProps';

import SearchRound from '@vicons/material/SearchRound';
import UndoRound from '@vicons/material/UndoRound';

const { users, error, load: loadUsers } = useUsersAdmin();
const { message } = useMessages();
const dialog = useDialog();
const route = useRoute();
const auth = useAuthStore();

const pagination = ref({
  page: 1,
  pageSize: 10,
});

const initialFilters = () => ({
  search: '',
  isActive: true,
  isInactive: true,
  isVerified: true,
  isUnverified: true,
  isSuperuser: true,
  isNoSuperuser: true,
});

const filters = ref(initialFilters());

function filterData(users: UserRead[]) {
  pagination.value.page = 1;
  return users.filter((u) => {
    const userStringContent = filters.value.search
      ? [u.username, u.email, u.firstName, u.lastName, u.affiliation, u.createdAt].join(' ')
      : '';
    return (
      (!filters.value.search ||
        userStringContent.toLowerCase().includes(filters.value.search.toLowerCase())) &&
      ((filters.value.isActive && u.isActive) || (filters.value.isInactive && !u.isActive)) &&
      ((filters.value.isVerified && u.isVerified) ||
        (filters.value.isUnverified && !u.isVerified)) &&
      ((filters.value.isSuperuser && u.isSuperuser) ||
        (filters.value.isNoSuperuser && !u.isSuperuser))
    );
  });
}

const filteredData = computed(() => filterData(users.value || []));
const paginatedData = computed(() => {
  const start = (pagination.value.page - 1) * pagination.value.pageSize;
  const end = start + pagination.value.pageSize;
  return filteredData.value.slice(start, end);
});

async function updateUser(user: UserRead, updates: UserUpdate) {
  const { data: updatedUser, error } = await PATCH('/users/{id}', {
    params: { path: { id: user.id } },
    body: updates,
  });
  if (!error) {
    message.success($t('admin.users.save', { username: user.username }));
    loadUsers();
    filters.value = initialFilters();
    return updatedUser;
  } else {
    message.error($t('errors.unexpected'), error);
  }
}

function handleSuperuserClick(user: UserRead) {
  dialog.warning({
    title: $t('general.warning'),
    content: user.isSuperuser
      ? $t('admin.users.confirmMsg.setUser', { username: user.username })
      : $t('admin.users.confirmMsg.setSuperuser', { username: user.username }),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: () => updateUser(user, { isSuperuser: !user.isSuperuser }),
  });
}

function handleActiveClick(user: UserRead) {
  dialog.warning({
    title: $t('general.warning'),
    content: user.isActive
      ? $t('admin.users.confirmMsg.setInactive', { username: user.username })
      : $t('admin.users.confirmMsg.setActive', { username: user.username }),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      const updatedUser = await updateUser(user, { isActive: !user.isActive });
      // if just activated but still unverified, send verification mail
      if (updatedUser && updatedUser.isActive && !updatedUser.isVerified) {
        const { error } = await POST('/auth/request-verify-token', {
          body: { email: updatedUser.email },
        });
        if (!error) {
          message.info(
            $t('admin.users.msgSentVerificationLink', { username: updatedUser.username })
          );
        } else {
          message.error($t('admin.users.msgSentVerificationLinkError'), error.detail?.toString());
        }
      }
    },
  });
}

function handleVerifiedClick(user: UserRead) {
  dialog.warning({
    title: $t('general.warning'),
    content: user.isVerified
      ? $t('admin.users.confirmMsg.setUnverified', { username: user.username })
      : $t('admin.users.confirmMsg.setVerified', { username: user.username }),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      const updatedUser = await updateUser(user, { isVerified: !user.isVerified });
      if (updatedUser && !updatedUser.isVerified) {
        const { error } = await POST('/auth/request-verify-token', {
          body: { email: updatedUser.email },
        });
        if (!error) {
          message.info(
            $t('admin.users.msgSentVerificationLink', { username: updatedUser.username })
          );
        } else {
          message.error($t('admin.users.msgSentVerificationLinkError'), error.detail?.toString());
        }
      }
    },
  });
}

function handleDeleteClick(user: UserRead) {
  dialog.warning({
    title: $t('general.warning'),
    content: $t('admin.users.confirmMsg.deleteUser', { username: user.username }),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      const { error } = await DELETE('/users/{id}', { params: { path: { id: user.id } } });
      if (!error) {
        message.success($t('admin.users.msgUserDeleted', { username: user.username }));
        loadUsers();
      } else {
        message.error($t('errors.unexpected'), error);
      }
    },
  });
}

function handleFilterCollapseItemClick(data: { name: string; expanded: boolean }) {
  if (data.name === 'filters' && !data.expanded) {
    filters.value = initialFilters();
  }
}

onMounted(() => {
  if (route.query.search) {
    filters.value.search = route.query.search?.toString();
  }
});
</script>

<template>
  <h2>
    {{ $t('admin.users.heading') }}
    <HelpButtonWidget help-key="adminSystemUsersView" />
  </h2>

  <template v-if="users && !error">
    <!-- Filters -->
    <n-collapse
      style="margin-bottom: var(--layout-gap)"
      @item-header-click="handleFilterCollapseItemClick"
    >
      <n-collapse-item :title="$t('general.filters')" name="filters">
        <n-input
          v-model:value="filters.search"
          :placeholder="$t('search.searchAction')"
          style="margin-bottom: var(--layout-gap)"
          round
        >
          <template #prefix>
            <n-icon :component="SearchRound" />
          </template>
        </n-input>
        <n-space vertical justify="space-between" style="padding-left: var(--layout-gap)">
          <n-checkbox v-model:checked="filters.isActive" :label="$t('models.user.isActive')" />
          <n-checkbox v-model:checked="filters.isInactive" :label="$t('models.user.isInactive')" />
          <n-checkbox v-model:checked="filters.isVerified" :label="$t('models.user.isVerified')" />
          <n-checkbox
            v-model:checked="filters.isUnverified"
            :label="$t('models.user.isUnverified')"
          />
          <n-checkbox
            v-model:checked="filters.isSuperuser"
            :label="$t('models.user.isSuperuser')"
          />
          <n-checkbox
            v-model:checked="filters.isNoSuperuser"
            :label="$t('models.user.modelLabel')"
          />
          <n-button
            secondary
            round
            style="margin-top: var(--content-gap)"
            @click="filters = initialFilters()"
          >
            {{ $t('general.resetAction') }}
            <template #icon>
              <n-icon :component="UndoRound" />
            </template>
          </n-button>
        </n-space>
      </n-collapse-item>
    </n-collapse>
    <!-- Users List -->
    <div class="content-block">
      <template v-if="paginatedData.length > 0">
        <n-list style="background-color: transparent">
          <user-list-item
            v-for="user in paginatedData"
            :key="user.id"
            :target-user="user"
            :current-user="auth.user"
            @active-click="handleActiveClick"
            @verified-click="handleVerifiedClick"
            @superuser-click="handleSuperuserClick"
            @delete-click="handleDeleteClick"
          />
        </n-list>
        <!-- Pagination -->
        <div style="display: flex; justify-content: flex-end; padding-top: 12px">
          <n-pagination
            v-model:page-size="pagination.pageSize"
            v-model:page="pagination.page"
            :page-sizes="[10, 20, 50, 100]"
            :default-page-size="10"
            :item-count="filteredData.length"
            show-size-picker
          />
        </div>
      </template>
      <template v-else>
        {{ $t('search.nothingFound') }}
      </template>
    </div>
  </template>

  <n-spin
    v-else-if="!users && !error"
    size="large"
    style="margin: 3rem 0 2rem 0; width: 100%"
    :description="$t('init.loading')"
  />

  <div v-else>
    {{ $t('errors.error') }}
  </div>
</template>
