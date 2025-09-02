<script setup lang="ts">
import type { UserRead, UserSearchFilters, UserUpdate } from '@/api';
import { DELETE, PATCH, POST } from '@/api';
import { dialogProps } from '@/common';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import ListingsFilters from '@/components/ListingsFilters.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import UserListItem from '@/components/user/UserListItem.vue';
import { useAdminUserSearch } from '@/composables/adminUserSearch';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { ErrorIcon, NewUserIcon, NoContentIcon, UsersIcon } from '@/icons';
import { useAuthStore, useStateStore } from '@/stores';
import { createReusableTemplate } from '@vueuse/core';
import { NButton, NEmpty, NFlex, NIcon, NList, NPagination, NSpin, useDialog } from 'naive-ui';
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const { message } = useMessages();
const dialog = useDialog();
const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const state = useStateStore();
const [DefineTemplate, ReuseTemplate] = createReusableTemplate();

const filtersRef = ref<InstanceType<typeof ListingsFilters> | null>(null);
const filtersSearch = ref<string>();
const filtersFlags = ref<string[]>();
const page = ref(1);
const pageSize = ref(10);
const filters = computed<UserSearchFilters>(() => ({
  q: filtersSearch.value,
  active: filtersFlags.value?.includes('active'),
  inactive: filtersFlags.value?.includes('inactive'),
  verified: filtersFlags.value?.includes('verified'),
  unverified: filtersFlags.value?.includes('unverified'),
  admin: filtersFlags.value?.includes('admin'),
  user: filtersFlags.value?.includes('user'),
  pg: page.value,
  pgs: pageSize.value,
}));

const { users, total, error, loading } = useAdminUserSearch(filters);

function resetPagination() {
  filters.value.pg = 1;
}

async function updateUser(user: UserRead, updates: UserUpdate) {
  const { data: updatedUser, error } = await PATCH('/users/{id}', {
    params: { path: { id: user.id } },
    body: updates,
  });
  if (!error) {
    message.success($t('admin.users.save', { username: user.username }));
    filtersRef.value?.reset();
    resetPagination();
    return updatedUser;
  }
}

function handleSetSuperuserClick(user: UserRead, setSuperuser: boolean) {
  dialog.warning({
    title: $t('common.warning'),
    content: user.isSuperuser
      ? $t('admin.users.confirmMsg.setUser', { username: user.username })
      : $t('admin.users.confirmMsg.setSuperuser', { username: user.username }),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
    closable: false,
    ...dialogProps,
    onPositiveClick: () => updateUser(user, { isSuperuser: setSuperuser }),
  });
}

function handleActiveClick(user: UserRead, setActive: boolean) {
  dialog.warning({
    title: $t('common.warning'),
    content: user.isActive
      ? $t('admin.users.confirmMsg.setInactive', { username: user.username })
      : $t('admin.users.confirmMsg.setActive', { username: user.username }),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      const updatedUser = await updateUser(user, { isActive: setActive });
      // if just activated but still unverified, send verification mail
      if (updatedUser && updatedUser.isActive && !updatedUser.isVerified) {
        const { error } = await POST('/auth/request-verify-token', {
          body: { email: updatedUser.email },
        });
        if (!error) {
          message.info(
            $t('admin.users.msgSentVerificationLink', { username: updatedUser.username })
          );
        }
      }
    },
  });
}

function handleVerifiedClick(user: UserRead, setVerified: boolean) {
  dialog.warning({
    title: $t('common.warning'),
    content: user.isVerified
      ? $t('admin.users.confirmMsg.setUnverified', { username: user.username })
      : $t('admin.users.confirmMsg.setVerified', { username: user.username }),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      const updatedUser = await updateUser(user, { isVerified: setVerified });
      if (updatedUser && !updatedUser.isVerified) {
        const { error } = await POST('/auth/request-verify-token', {
          body: { email: updatedUser.email },
        });
        if (!error) {
          message.info(
            $t('admin.users.msgSentVerificationLink', { username: updatedUser.username })
          );
        }
      }
    },
  });
}

function handleDeleteClick(user: UserRead) {
  dialog.warning({
    title: $t('common.warning'),
    content: $t('admin.users.confirmMsg.deleteUser', { username: user.username }),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      const { error } = await DELETE('/users/{id}', { params: { path: { id: user.id } } });
      if (!error) {
        message.success($t('admin.users.msgUserDeleted', { username: user.username }));
        filtersRef.value?.reset();
        resetPagination();
      }
    },
  });
}

function handleRegister() {
  router.push({ name: 'register' });
}

onMounted(() => {
  if (route.query.search) {
    filters.value.q = route.query.search?.toString();
  }
});
</script>

<template>
  <icon-heading level="1" :icon="UsersIcon">
    {{ $t('admin.users.heading') }}
    <help-button-widget help-key="adminUsersView" />
  </icon-heading>

  <define-template>
    <!-- Pagination -->
    <n-flex v-if="!!total" justify="end">
      <n-pagination
        v-model:page="page"
        v-model:page-size="pageSize"
        :simple="state.smallScreen"
        :default-page-size="10"
        :page-slot="state.smallScreen ? 4 : 9"
        :disabled="loading"
        :item-count="total"
        :page-sizes="[10, 25, 50]"
        size="medium"
        show-size-picker
      />
    </n-flex>
  </define-template>

  <!-- Filters -->
  <listings-filters
    ref="filtersRef"
    v-model:search="filtersSearch"
    v-model:flags="filtersFlags"
    :flags-labels="{
      active: $t('models.user.isActive'),
      inactive: $t('models.user.isInactive'),
      verified: $t('models.user.isVerified'),
      unverified: $t('models.user.isUnverified'),
      admin: $t('models.user.isSuperuser'),
      user: $t('models.user.modelLabel'),
    }"
  />

  <n-spin v-if="loading" class="centered-spinner" :description="$t('common.loading')" />
  <n-empty v-else-if="error" :description="$t('errors.unexpected')">
    <template #icon>
      <n-icon :component="ErrorIcon" />
    </template>
  </n-empty>

  <template v-else-if="total">
    <n-flex justify="space-between">
      <span class="text-small translucent">{{
        $t('admin.users.msgFoundCount', { count: total })
      }}</span>
      <n-button v-if="!!state.pf?.security.closedMode" type="primary" @click="handleRegister">
        <template #icon>
          <n-icon :component="NewUserIcon" />
        </template>
        {{ $t('admin.users.registerNewUser') }}
      </n-button>
    </n-flex>

    <!-- Users List -->
    <div class="content-block">
      <template v-if="!!total">
        <!-- Pagination -->
        <reuse-template />
        <n-list class="my-lg" style="background-color: transparent">
          <user-list-item
            v-for="user in users"
            :key="user.id"
            :target-user="user"
            :platform-name="state.pf?.state.platformName || 'Tekst'"
            :current-user="auth.user"
            @activate-click="handleActiveClick"
            @verify-click="handleVerifiedClick"
            @set-superuser-click="handleSetSuperuserClick"
            @delete-click="handleDeleteClick"
          />
        </n-list>
        <!-- Pagination -->
        <reuse-template />
      </template>
      <template v-else>
        {{ $t('search.nothingFound') }}
      </template>
    </div>
  </template>

  <n-empty v-else :description="$t('admin.users.msgFoundCount', { count: total })">
    <template #icon>
      <n-icon :component="NoContentIcon" />
    </template>
  </n-empty>
</template>
