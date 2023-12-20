<script setup lang="ts">
import { UserSelectTemplatePromise } from '@/templatePromises';
import { NSelect, NButton, NModal, NFormItem, type SelectOption } from 'naive-ui';
import ButtonFooter from './ButtonFooter.vue';
import { computed, h, ref, type VNodeChild } from 'vue';
import { useUsersSearch } from '@/fetchers';
import type { UserReadPublic } from '@/api';
import UserDisplayText from '@/components/UserDisplayText.vue';

const value = ref();
const userSearchQuery = ref();
const { users, loading, error } = useUsersSearch(userSearchQuery);

const usersOptions = computed(() => users.value.map((u) => ({ value: u.id, user: u })));

function renderUserSelectLabel(option: SelectOption): VNodeChild {
  return h(UserDisplayText, { user: option.user as UserReadPublic });
}

function handleOkClick(resolve: (v: UserReadPublic) => void, reject: (v: any) => void) {
  const user = usersOptions.value.find((o) => o.value === value.value)?.user;
  if (user) {
    resolve(user);
  } else {
    return reject(null);
  }
}
</script>

<template>
  <UserSelectTemplatePromise v-slot="{ args, resolve, reject }">
    <n-modal
      :show="true"
      preset="card"
      class="tekst-modal"
      size="medium"
      :bordered="false"
      :closable="false"
      to="#app-container"
      :title="args[0]"
      embedded
      @close="reject(null)"
      @mask-click="reject(null)"
      @esc="reject(null)"
    >
      <n-form-item :label="args[1]">
        <n-select
          v-model:value="value"
          filterable
          clearable
          remote
          clear-filter-after-select
          :loading="loading"
          :render-label="renderUserSelectLabel"
          :status="error ? 'error' : undefined"
          :options="usersOptions"
          :placeholder="$t('resources.phSearchUsers')"
          @search="(q) => (userSearchQuery = q)"
          @keydown.enter.prevent
        />
      </n-form-item>
      <ButtonFooter>
        <n-button secondary @click="reject(null)">
          {{ $t('general.cancelAction') }}
        </n-button>
        <n-button type="primary" @click="handleOkClick(resolve, reject)">
          {{ $t('general.okAction') }}
        </n-button>
      </ButtonFooter>
    </n-modal>
  </UserSelectTemplatePromise>
</template>
