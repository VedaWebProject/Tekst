<script setup lang="ts">
import type { AnyResourceRead, PublicUserSearchFilters, UserReadPublic } from '@/api';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import UserDisplay from '@/components/user/UserDisplay.vue';
import { useMessages } from '@/composables/messages';
import { usePublicUserSearch } from '@/composables/publicUserSearch';
import { $t } from '@/i18n';
import { UserIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import {
  NAlert,
  NButton,
  NForm,
  NFormItem,
  NSelect,
  type FormInst,
  type FormItemRule,
  type SelectOption,
} from 'naive-ui';
import { computed, h, ref, type VNodeChild } from 'vue';

const props = defineProps<{ resource?: AnyResourceRead; loading?: boolean }>();
const emit = defineEmits(['submit']);
const show = defineModel<boolean>('show');

const state = useStateStore();
const { message } = useMessages();

const initialUserSearchQuery = (): PublicUserSearchFilters => ({
  pg: 1,
  pgs: 9999,
  emptyOk: false,
});

const resourceTitle = computed(() => pickTranslation(props.resource?.title, state.locale));
const formModel = ref<{ userId: string | undefined }>({ userId: undefined });
const formRef = ref<FormInst | null>(null);
const userSearchQuery = ref<PublicUserSearchFilters>(initialUserSearchQuery());
const { users, loading: loadingSearch, error } = usePublicUserSearch(userSearchQuery);

const usersOptions = computed(() =>
  users.value.map((u) => ({
    value: u.id,
    user: u,
    disabled: (props.resource?.public && !u.isSuperuser) || props.resource?.ownerId === u.id,
  }))
);

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
  return h(UserDisplay, { user: option.user as UserReadPublic, link: false });
}

async function handleOkClick() {
  await formRef.value
    ?.validate((errors) => {
      if (errors) return;
      const user = usersOptions.value.find((o) => o.value === formModel.value.userId)?.user;
      if (user) {
        emit('submit', props.resource, user);
      } else {
        show.value = false;
      }
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    });
  formModel.value = { userId: undefined };
  userSearchQuery.value = initialUserSearchQuery();
}
</script>

<template>
  <generic-modal
    :show="show && !!resource"
    :title="$t('resources.transferAction')"
    :icon="UserIcon"
    @update:show="(v) => (show = v)"
  >
    <n-alert type="warning" :title="$t('common.warning')" class="mb-lg">
      {{ $t('resources.warnTransfer') }}
    </n-alert>
    <div class="mb-lg">{{ resourceTitle }} – {{ $t('resources.transferAction') }}:</div>
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
          @search="(q) => (userSearchQuery.q = q)"
        />
      </n-form-item>
    </n-form>
    <button-shelf top-gap>
      <n-button secondary :disabled="loading" @click="show = false">
        {{ $t('common.cancel') }}
      </n-button>
      <n-button
        type="primary"
        :disabled="!formModel.userId || loading || loadingSearch"
        :loading="loading"
        @click="handleOkClick"
      >
        {{ $t('common.ok') }}
      </n-button>
    </button-shelf>
  </generic-modal>
</template>
