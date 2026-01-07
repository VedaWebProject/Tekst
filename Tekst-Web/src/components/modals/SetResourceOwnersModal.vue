<script setup lang="ts">
import type { AnyResourceRead, PublicUserSearchFilters, UserReadPublic } from '@/api';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import UserDisplay from '@/components/user/UserDisplay.vue';
import { useMessages } from '@/composables/messages';
import { usePublicUserSearch } from '@/composables/user';
import { resourceOwnershipRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { UserIcon } from '@/icons';
import { useAuthStore, useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { isEqual } from 'lodash-es';
import {
  NAlert,
  NButton,
  NForm,
  NFormItem,
  NSelect,
  type FormInst,
  type SelectOption,
} from 'naive-ui';
import { computed, h, ref, shallowRef, type VNodeChild } from 'vue';

defineProps<{ loading?: boolean }>();
const emit = defineEmits(['submit']);

const state = useStateStore();
const auth = useAuthStore();
const { message } = useMessages();

const showModal = shallowRef(false);
const resource = shallowRef<AnyResourceRead>();
const initialUserSearchQuery = (): PublicUserSearchFilters => ({
  pg: 1,
  pgs: 9999,
  emptyOk: true,
});

const resourceTitle = computed(() => pickTranslation(resource.value?.title, state.locale));
const formModel = ref<{ ownerIds: string[] | undefined }>({ ownerIds: resource.value?.ownerIds });
const formRef = ref<FormInst | null>(null);
const userSearchQuery = ref<PublicUserSearchFilters>(initialUserSearchQuery());
const { users, loading: loadingSearch, error } = usePublicUserSearch(userSearchQuery);

const usersOptions = computed(() =>
  users.value.map((u) => ({
    value: u.id,
    user: u,
    disabled: resource.value?.public && !u.isSuperuser,
  }))
);

function show(nextResource: AnyResourceRead) {
  resource.value = nextResource;
  formModel.value.ownerIds = nextResource.ownerIds;
  showModal.value = true;
}

function renderUserSelectLabel(option: SelectOption): VNodeChild {
  return h(UserDisplay, { user: option.user as UserReadPublic, link: false });
}

async function handleSaveClick() {
  await formRef.value
    ?.validate((errors) => {
      if (errors) return;
      emit('submit', resource.value, formModel.value.ownerIds || []);
      showModal.value = false;
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    });
  formModel.value = { ownerIds: undefined };
  userSearchQuery.value = initialUserSearchQuery();
}

defineExpose({ show });
</script>

<template>
  <generic-modal
    :show="showModal && !!resource"
    :title="$t('resources.setOwnersAction')"
    :icon="UserIcon"
    @update:show="(v) => (showModal = v)"
  >
    <n-alert
      v-if="!auth.user?.isSuperuser"
      type="warning"
      :title="$t('common.warning')"
      class="mb-lg"
    >
      {{ $t('resources.warnSetOwners') }}
    </n-alert>
    <div class="mb-lg">
      <b>{{ $t('models.resource.modelLabel') }}:</b> {{ resourceTitle }}
    </div>

    <n-form
      ref="formRef"
      :model="formModel"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
      class="gray-box"
      :rules="resourceOwnershipRules"
    >
      <n-form-item path="ownerIds" :label="$t('models.resource.owners')">
        <n-select
          v-model:value="formModel.ownerIds"
          filterable
          multiple
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
      <n-button secondary :disabled="loading" @click="showModal = false">
        {{ $t('common.cancel') }}
      </n-button>
      <n-button
        type="primary"
        :disabled="loading || loadingSearch || isEqual(formModel.ownerIds, resource?.ownerIds)"
        :loading="loading"
        @click="handleSaveClick"
      >
        {{ $t('common.save') }}
      </n-button>
    </button-shelf>
  </generic-modal>
</template>
