<script setup lang="ts">
import type { UserRead, UserSearchFilters, UserUpdate } from '@/api';
import { DELETE, PATCH, POST } from '@/api';
import { dialogProps } from '@/common';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import LabeledSwitch from '@/components/LabeledSwitch.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import UserListItem from '@/components/user/UserListItem.vue';
import { useAdminUserSearch } from '@/composables/adminUserSearch';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { ErrorIcon, FilterIcon, NoContentIcon, SearchIcon, UndoIcon, UsersIcon } from '@/icons';
import { useAuthStore, useStateStore } from '@/stores';
import { createReusableTemplate } from '@vueuse/core';
import {
  NButton,
  NCollapse,
  NCollapseItem,
  NEmpty,
  NFlex,
  NIcon,
  NInput,
  NList,
  NPagination,
  NSpin,
  useDialog,
} from 'naive-ui';
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

const { message } = useMessages();
const dialog = useDialog();
const route = useRoute();
const auth = useAuthStore();
const state = useStateStore();
const [DefineTemplate, ReuseTemplate] = createReusableTemplate();

const defaultPage = 1;
const paginationSlots = computed(() => (state.smallScreen ? 4 : 9));

const initialFilters = (): UserSearchFilters => ({
  q: '',
  active: true,
  inactive: true,
  verified: true,
  unverified: true,
  admin: true,
  user: true,
  pg: defaultPage,
  pgs: 10,
});

const filters = ref<UserSearchFilters>(initialFilters());
const { users, total, error, loading } = useAdminUserSearch(filters);

function resetPagination() {
  filters.value.pg = defaultPage;
}

async function updateUser(user: UserRead, updates: UserUpdate) {
  const { data: updatedUser, error } = await PATCH('/users/{id}', {
    params: { path: { id: user.id } },
    body: updates,
  });
  if (!error) {
    message.success($t('admin.users.save', { username: user.username }));
    filters.value = initialFilters();
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
        filters.value = initialFilters();
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
        v-model:page="filters.pg"
        v-model:page-size="filters.pgs"
        :simple="state.smallScreen"
        :default-page-size="10"
        :page-slot="paginationSlots"
        :disabled="loading"
        :item-count="total"
        :page-sizes="[10, 25, 50]"
        size="medium"
        show-size-picker
      />
    </n-flex>
  </define-template>

  <!-- Filters -->
  <n-collapse class="mb-lg" @item-header-click="handleFilterCollapseItemClick">
    <n-collapse-item name="filters">
      <template #header>
        <n-flex align="center" :wrap="false">
          <n-icon :component="FilterIcon" class="translucent" />
          <span>{{ $t('common.filters') }}</span>
        </n-flex>
      </template>
      <n-flex vertical size="small" class="gray-box" style="padding-left: var(--gap-lg)">
        <n-input
          v-model:value="filters.q"
          :placeholder="$t('common.searchAction')"
          class="mb-md"
          round
          clearable
          @update:value="resetPagination"
        >
          <template #prefix>
            <n-icon :component="SearchIcon" />
          </template>
        </n-input>

        <labeled-switch
          v-model="filters.active"
          :label="$t('models.user.isActive')"
          @update:model-value="resetPagination"
        />
        <labeled-switch
          v-model="filters.inactive"
          :label="$t('models.user.isInactive')"
          @update:model-value="resetPagination"
        />
        <labeled-switch
          v-model="filters.verified"
          :label="$t('models.user.isVerified')"
          @update:model-value="resetPagination"
        />
        <labeled-switch
          v-model="filters.unverified"
          :label="$t('models.user.isUnverified')"
          @update:model-value="resetPagination"
        />
        <labeled-switch
          v-model="filters.admin"
          :label="$t('models.user.isSuperuser')"
          @update:model-value="resetPagination"
        />
        <labeled-switch
          v-model="filters.user"
          :label="$t('models.user.modelLabel')"
          @update:model-value="resetPagination"
        />

        <n-button secondary class="mt-md" @click="filters = initialFilters()">
          {{ $t('common.reset') }}
          <template #icon>
            <n-icon :component="UndoIcon" />
          </template>
        </n-button>
      </n-flex>
    </n-collapse-item>
  </n-collapse>

  <n-spin v-if="loading" class="centered-spinner" :description="$t('common.loading')" />

  <n-empty v-else-if="error" :description="$t('errors.unexpected')">
    <template #icon>
      <n-icon :component="ErrorIcon" />
    </template>
  </n-empty>

  <template v-else-if="total">
    <div class="text-small translucent">
      {{ $t('admin.users.msgFoundCount', { count: total }) }}
    </div>

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
