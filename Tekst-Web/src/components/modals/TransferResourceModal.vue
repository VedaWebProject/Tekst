<script setup lang="ts">
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
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import { computed, h, ref, type VNodeChild } from 'vue';
import { useUsersSearch } from '@/composables/fetchers';
import type { AnyResourceRead, UserReadPublic } from '@/api';
import UserDisplayText from '@/components/user/UserDisplayText.vue';
import { $t } from '@/i18n';
import { useMessages } from '@/composables/messages';
import GenericModal from '@/components/generic/GenericModal.vue';

import { UserIcon } from '@/icons';

const props = defineProps<{ show?: boolean; resource?: AnyResourceRead; loading?: boolean }>();
const emit = defineEmits(['update:show', 'submit']);

const { message } = useMessages();
const formModel = ref<{ userId: string | undefined }>({ userId: undefined });
const formRef = ref<FormInst | null>(null);
const userSearchQuery = ref<string>();
const { users, loading: loadingSearch, error } = useUsersSearch(userSearchQuery);

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

async function handleOkClick() {
  await formRef.value
    ?.validate((errors) => {
      if (errors) return;
      const user = usersOptions.value.find((o) => o.value === formModel.value.userId)?.user;
      if (user) {
        emit('submit', props.resource, user);
      } else {
        emit('update:show', false);
      }
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    });
  formModel.value = { userId: undefined };
  userSearchQuery.value = undefined;
}
</script>

<template>
  <GenericModal
    :show="show && !!resource"
    :title="$t('resources.transferAction')"
    :icon="UserIcon"
    @update:show="emit('update:show', $event)"
  >
    <n-alert type="warning" :title="$t('general.warning')" style="margin-bottom: var(--layout-gap)">
      {{ $t('resources.warnTransfer') }}
    </n-alert>
    <div style="margin-bottom: var(--layout-gap)">
      {{ resource?.title }} – {{ $t('resources.transferAction') }}:
    </div>
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
          :loading="loadingSearch"
          :disabled="loading"
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
      <n-button secondary :disabled="loading" @click="emit('update:show', false)">
        {{ $t('general.cancelAction') }}
      </n-button>
      <n-button
        type="primary"
        :disabled="!formModel.userId || loading || loadingSearch"
        :loading="loading"
        @click="handleOkClick"
      >
        {{ $t('general.okAction') }}
      </n-button>
    </ButtonShelf>
  </GenericModal>
</template>
