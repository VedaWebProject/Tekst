<script setup lang="ts">
import { onMounted } from 'vue';
import { useUsers } from '@/fetchers';
import { NButton, NInput, NIcon, NCheckbox, NSpace, NSpin, NPagination, NList } from 'naive-ui';
import UserListItem from '@/views/admin/UserListItem.vue';
import { hashCode } from '@/utils';
import type { UserRead } from '@/openapi';
import { ref } from 'vue';
import { computed } from 'vue';
import { useMessages } from '@/messages';
import { useI18n } from 'vue-i18n';

import SearchRound from '@vicons/material/SearchRound';
import UndoRound from '@vicons/material/UndoRound';
import { useRoute } from 'vue-router';

const { t } = useI18n({ useScope: 'global' });
const { users, error, load: loadUsers } = useUsers();
const { message } = useMessages();
const route = useRoute();

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

function handleUserUpdated(updatedUser: UserRead) {
  message.success(t('admin.users.save', { username: updatedUser.username }));
  loadUsers();
}

onMounted(() => {
  if (route.query.search) {
    filters.value.search = route.query.search?.toString();
  }
});
</script>

<template>
  <h1>{{ $t('admin.heading') }}: {{ $t('admin.users.heading') }}</h1>

  <template v-if="users && !error">
    <!-- Filters -->
    <div style="margin-bottom: 1.5rem">
      <n-input
        v-model:value="filters.search"
        :placeholder="t('search.searchAction')"
        style="margin-bottom: 1rem"
        round
      >
        <template #prefix>
          <n-icon :component="SearchRound" />
        </template>
      </n-input>
      <n-space justify="space-between">
        <n-checkbox v-model:checked="filters.isActive" :label="t('models.user.isActive')" />
        <n-checkbox v-model:checked="filters.isInactive" :label="t('models.user.isInactive')" />
        <n-checkbox v-model:checked="filters.isVerified" :label="t('models.user.isVerified')" />
        <n-checkbox v-model:checked="filters.isUnverified" :label="t('models.user.isUnverified')" />
        <n-checkbox v-model:checked="filters.isSuperuser" :label="t('models.user.isSuperuser')" />
        <n-checkbox v-model:checked="filters.isNoSuperuser" :label="t('models.user.modelLabel')" />
        <n-button secondary round @click="filters = initialFilters()">
          {{ t('general.resetAction') }}
          <template #icon>
            <n-icon :component="UndoRound" />
          </template>
        </n-button>
      </n-space>
    </div>
    <!-- Users List -->
    <div class="content-block" style="padding: var(--content-gap)">
      <template v-if="paginatedData.length > 0">
        <n-list style="background-color: transparent">
          <user-list-item
            v-for="item in paginatedData"
            :data="item"
            :key="hashCode(item)"
            @user-updated="handleUserUpdated"
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
        {{ t('search.nothingFound') }}
      </template>
    </div>
  </template>

  <n-spin
    v-else-if="!users && !error"
    style="margin: 3rem auto 2rem auto; display: flex"
    :description="$t('init.loading')"
  />

  <div v-else>
    {{ $t('errors.error') }}
  </div>
</template>

<style scoped></style>
