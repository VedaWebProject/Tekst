<script setup lang="ts">
import { TransferResourceTemplatePromise } from '@/templatePromises';
import {
  NForm,
  NAlert,
  NSelect,
  NButton,
  NFormItem,
  type SelectOption,
  type FormInst,
  type FormItemRule,
} from 'naive-ui';
import ButtonShelf from './ButtonShelf.vue';
import { computed, h, ref, type VNodeChild } from 'vue';
import { useUsersSearch } from '@/fetchers';
import type { UserReadPublic } from '@/api';
import UserDisplayText from '@/components/UserDisplayText.vue';
import { $t } from '@/i18n';
import { useMessages } from '@/messages';
import GenericModal from '@/components/GenericModal.vue';

import PersonFilled from '@vicons/material/PersonFilled';

const { message } = useMessages();
const formModel = ref<{ userId: string | undefined }>({ userId: undefined });
const formRef = ref<FormInst | null>(null);
const userSearchQuery = ref();
const { users, loading, error } = useUsersSearch(userSearchQuery);

const usersOptions = computed(() => users.value.map((u) => ({ value: u.id, user: u })));

const formRules: Record<string, FormItemRule[]> = {
  userId: [
    {
      required: true,
      message: () =>
        $t('forms.rulesFeedback.isRequired', {
          x: $t('models.user.modelLabel'),
        }),
      trigger: ['change', 'blur'],
    },
  ],
};

function renderUserSelectLabel(option: SelectOption): VNodeChild {
  return h(UserDisplayText, { user: option.user as UserReadPublic });
}

function handleOkClick(resolve: (v: UserReadPublic) => void, reject: (v: any) => void) {
  formRef.value
    ?.validate((errors) => {
      if (errors) return;
      const user = usersOptions.value.find((o) => o.value === formModel.value.userId)?.user;
      if (user) {
        resolve(user);
      } else {
        reject(null);
      }
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    });
}
</script>

<template>
  <TransferResourceTemplatePromise v-slot="{ resolve, reject }">
    <GenericModal
      show
      :title="$t('resources.transferAction')"
      :icon="PersonFilled"
      @close="reject(null)"
      @mask-click="reject(null)"
      @esc="reject(null)"
    >
      <n-alert
        type="warning"
        :title="$t('general.warning')"
        style="margin-bottom: var(--layout-gap)"
      >
        {{ $t('resources.warnTransfer') }}
      </n-alert>
      <n-form
        ref="formRef"
        :model="formModel"
        :rules="formRules"
        label-placement="top"
        label-width="auto"
        require-mark-placement="right-hanging"
      >
        <n-form-item path="userId" :label="$t('models.user.modelLabel')">
          <n-select
            v-model:value="formModel.userId"
            filterable
            remote
            clear-filter-after-select
            :loading="loading"
            :consistent-menu-width="false"
            :render-label="renderUserSelectLabel"
            :status="error ? 'error' : undefined"
            :options="usersOptions"
            :placeholder="$t('resources.phSearchUsers')"
            @search="(q) => (userSearchQuery = q)"
          />
        </n-form-item>
      </n-form>
      <ButtonShelf top-gap>
        <n-button secondary @click="reject(null)">
          {{ $t('general.cancelAction') }}
        </n-button>
        <n-button type="primary" @click="handleOkClick(resolve, reject)">
          {{ $t('general.okAction') }}
        </n-button>
      </ButtonShelf>
    </GenericModal>
  </TransferResourceTemplatePromise>
</template>
