<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useUsersAdmin } from '@/composables/fetchers';
import {
  NButton,
  NInput,
  NIcon,
  NFlex,
  NSpin,
  NPagination,
  NList,
  NCollapse,
  NCollapseItem,
  useDialog,
} from 'naive-ui';
import UserListItem from '@/components/user/UserListItem.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import type { UserRead, UserSearchFilters, UserUpdate } from '@/api';
import { ref } from 'vue';
import { useMessages } from '@/composables/messages';
import { $t } from '@/i18n';
import { useRoute } from 'vue-router';
import { POST, PATCH, DELETE } from '@/api';
import { useAuthStore, useStateStore } from '@/stores';
import { dialogProps } from '@/common';
import { ErrorIcon, NoContentIcon, SearchIcon, UndoIcon, UsersIcon } from '@/icons';
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import { createReusableTemplate } from '@vueuse/core';

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
const { users, total, error, loading } = useUsersAdmin(filters);

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
    title: $t('general.warning'),
    content: user.isSuperuser
      ? $t('admin.users.confirmMsg.setUser', { username: user.username })
      : $t('admin.users.confirmMsg.setSuperuser', { username: user.username }),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    autoFocus: false,
    closable: false,
    ...dialogProps,
    onPositiveClick: () => updateUser(user, { isSuperuser: setSuperuser }),
  });
}

function handleActiveClick(user: UserRead, setActive: boolean) {
  dialog.warning({
    title: $t('general.warning'),
    content: user.isActive
      ? $t('admin.users.confirmMsg.setInactive', { username: user.username })
      : $t('admin.users.confirmMsg.setActive', { username: user.username }),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    autoFocus: false,
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
    title: $t('general.warning'),
    content: user.isVerified
      ? $t('admin.users.confirmMsg.setUnverified', { username: user.username })
      : $t('admin.users.confirmMsg.setVerified', { username: user.username }),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    autoFocus: false,
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
    title: $t('general.warning'),
    content: $t('admin.users.confirmMsg.deleteUser', { username: user.username }),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    autoFocus: false,
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
  <icon-heading level="2" :icon="UsersIcon">
    {{ $t('admin.users.heading') }}
    <help-button-widget help-key="adminSystemUsersView" />
  </icon-heading>

  <define-template>
    <!-- Pagination -->
    <n-flex v-if="!!total" justify="end">
      <n-pagination
        v-model:page="filters.pg"
        v-model:page-size="filters.pgs"
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
  <n-collapse
    style="margin-bottom: var(--layout-gap)"
    @item-header-click="handleFilterCollapseItemClick"
  >
    <n-collapse-item :title="$t('general.filters')" name="filters">
      <n-flex vertical class="gray-box" style="padding-left: var(--layout-gap)">
        <n-input
          v-model:value="filters.q"
          :placeholder="$t('search.searchAction')"
          style="margin-bottom: var(--content-gap)"
          round
          clearable
          @update:value="resetPagination"
        >
          <template #prefix>
            <n-icon :component="SearchIcon" />
          </template>
        </n-input>

        <labelled-switch
          v-model="filters.active"
          :label="$t('models.user.isActive')"
          @update:model-value="resetPagination"
        />
        <labelled-switch
          v-model="filters.inactive"
          :label="$t('models.user.isInactive')"
          @update:model-value="resetPagination"
        />
        <labelled-switch
          v-model="filters.verified"
          :label="$t('models.user.isVerified')"
          @update:model-value="resetPagination"
        />
        <labelled-switch
          v-model="filters.unverified"
          :label="$t('models.user.isUnverified')"
          @update:model-value="resetPagination"
        />
        <labelled-switch
          v-model="filters.admin"
          :label="$t('models.user.isSuperuser')"
          @update:model-value="resetPagination"
        />
        <labelled-switch
          v-model="filters.user"
          :label="$t('models.user.modelLabel')"
          @update:model-value="resetPagination"
        />

        <n-button style="margin-top: var(--content-gap)" @click="filters = initialFilters()">
          {{ $t('general.resetAction') }}
          <template #icon>
            <n-icon :component="UndoIcon" />
          </template>
        </n-button>
      </n-flex>
    </n-collapse-item>
  </n-collapse>

  <n-spin
    v-if="loading"
    size="large"
    class="centered-spinner"
    :description="$t('general.loading')"
  />

  <huge-labelled-icon v-else-if="error" :message="$t('errors.unexpected')" :icon="ErrorIcon" />

  <template v-else-if="total">
    <div class="text-small translucent">
      {{ $t('admin.users.msgFoundCount', { count: total }) }}
    </div>

    <!-- Users List -->
    <div class="content-block">
      <template v-if="!!total">
        <!-- Pagination -->
        <reuse-template />
        <n-list style="background-color: transparent; margin: var(--layout-gap) 0">
          <user-list-item
            v-for="user in users"
            :key="user.id"
            :target-user="user"
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

  <huge-labelled-icon
    v-else
    :message="$t('admin.users.msgFoundCount', { count: total })"
    :icon="NoContentIcon"
  />
</template>
