<script setup lang="ts">
import { DELETE, POST } from '@/api';
import { accountFormRules } from '@/forms/formRules';
import { useMessages } from '@/composables/messages';
import { usePlatformData } from '@/composables/platformData';
import { useAuthStore } from '@/stores';
import type { FormInst, FormItemInst, FormItemRule } from 'naive-ui';
import { NButton, NInput, NFormItem, NForm, useDialog, NSpace } from 'naive-ui';
import { ref } from 'vue';
import { $t } from '@/i18n';
import { useModelChanges } from '@/composables/modelChanges';
import type { UserUpdate, UserUpdatePublicFields } from '@/api';
import { dialogProps } from '@/common';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import UserAvatar from '@/components/user/UserAvatar.vue';
import { ManageAccountIcon, NoImageIcon } from '@/icons';
import LabelledSwitch from '@/components/LabelledSwitch.vue';

const dialog = useDialog();
const auth = useAuthStore();
const { pfData } = usePlatformData();
const { message } = useMessages();

const initialEmailModel = () => ({
  email: auth.user?.email || null,
});

const initialPasswordModel = () => ({
  password: '',
  passwordRepeat: '',
});

const initialUserDataModel = () => ({
  username: auth.user?.username || null,
  name: auth.user?.name || null,
  affiliation: auth.user?.affiliation || null,
  avatarUrl: auth.user?.avatarUrl || null,
  bio: auth.user?.bio || null,
});

const initialPublicFieldsModel = () => ({
  name: auth.user?.publicFields?.includes('name') || false,
  affiliation: auth.user?.publicFields?.includes('affiliation') || false,
  bio: auth.user?.publicFields?.includes('bio') || false,
});

const emailFormRef = ref<FormInst | null>(null);
const emailFormModel = ref<Record<string, string | null>>(initialEmailModel());
const {
  changed: emailModelChanged,
  getChanges: getEmailModelChanges,
  reset: resetEmailModelChanges,
} = useModelChanges(emailFormModel);

const passwordFormRef = ref<FormInst | null>(null);
const passwordFormModel = ref<Record<string, string | null>>(initialPasswordModel());
const { changed: passwordModelChanged, reset: resetPasswordModelChanges } =
  useModelChanges(passwordFormModel);

const userDataFormRef = ref<FormInst | null>(null);
const userDataFormModel = ref<Record<string, string | null>>(initialUserDataModel());
const {
  changed: userDataModelChanged,
  getChanges: getUserDataModelChanges,
  reset: resetUserDataModelChanges,
} = useModelChanges(userDataFormModel);

const publicFieldsFormRef = ref<FormInst | null>(null);
const publicFieldsFormModel = ref<Record<string, boolean>>(initialPublicFieldsModel());
const { changed: publicFieldsModelChanged, reset: resetPublicFieldsModelChanges } =
  useModelChanges(publicFieldsFormModel);

const rPasswordFormItemRef = ref<FormItemInst | null>(null);
const deleteAccountSafetyInput = ref('');
const loading = ref(false);

const passwordRepeatMatchRule = {
  validator: (rule: FormItemRule, value: string) =>
    !!value && !!passwordFormModel.value.password && value === passwordFormModel.value.password,
  message: () => $t('models.user.formRulesFeedback.passwordRepNoMatch'),
  trigger: ['input', 'blur', 'password-input'],
};

function handlePasswordInput() {
  if (passwordFormModel.value.reenteredPassword) {
    rPasswordFormItemRef.value?.validate({ trigger: 'password-input' });
  }
}

async function updateUser(userUpdate: UserUpdate) {
  loading.value = true;
  const updatedUser = await auth.updateUser(userUpdate);
  loading.value = false;
  return updatedUser;
}

async function updateEmail() {
  if (!(await updateUser(getEmailModelChanges()))) return;
  emailFormModel.value = initialEmailModel();
  resetEmailModelChanges();
  message.success($t('account.manage.msgEmailSaveSuccess'));
  if (pfData.value?.security?.closedMode === true) return;
  await auth.logout();
  const { error } = await POST('/auth/request-verify-token', {
    body: { email: emailFormModel.value.email || '' },
  });
  if (!error) {
    message.warning($t('account.manage.msgVerifyEmailWarning'), undefined, 20);
  }
  auth.showLoginModal(
    $t('account.manage.msgVerifyEmailWarning'),
    { name: 'accountProfile' },
    false
  );
}

function handleEmailSave() {
  emailFormRef.value
    ?.validate(async (errors) => {
      if (!errors) {
        if (pfData.value?.security?.closedMode) {
          updateEmail();
        } else {
          dialog.warning({
            title: $t('general.warning'),
            content: $t('account.manage.msgEmailChangeWarning'),
            positiveText: $t('general.saveAction'),
            negativeText: $t('general.cancelAction'),
            autoFocus: false,
            closable: false,
            ...dialogProps,
            onPositiveClick: updateEmail,
          });
        }
      }
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    });
}

async function handlePasswordSave() {
  passwordFormRef.value
    ?.validate(async (errors) => {
      !errors &&
        dialog.warning({
          title: $t('general.warning'),
          content: $t('account.manage.msgPasswordChangeWarning'),
          positiveText: $t('general.saveAction'),
          negativeText: $t('general.cancelAction'),
          autoFocus: false,
          closable: false,
          ...dialogProps,
          onPositiveClick: async () => {
            if (
              !(await updateUser({
                password: passwordFormModel.value.password || undefined,
              }))
            )
              return;
            passwordFormModel.value = initialPasswordModel();
            resetPasswordModelChanges();
            message.success($t('account.manage.msgPasswordSaveSuccess'));
            await auth.logout();
            auth.showLoginModal(undefined, { name: 'accountProfile' }, false);
          },
        });
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    });
}

async function handleUserDataSave() {
  userDataFormRef.value
    ?.validate(async (validationErrors) => {
      if (!validationErrors) {
        if (!(await updateUser(getUserDataModelChanges()))) return;
        userDataFormModel.value = initialUserDataModel();
        resetUserDataModelChanges();
        message.success($t('account.manage.msgUserDataSaveSuccess'));
      }
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    });
}

async function handlepublicFieldsSave() {
  if (
    await updateUser({
      publicFields: Object.keys(publicFieldsFormModel.value).filter(
        (k) => publicFieldsFormModel.value[k]
      ) as UserUpdatePublicFields,
    })
  ) {
    publicFieldsFormModel.value = initialPublicFieldsModel();
    resetPublicFieldsModelChanges();
    message.success($t('account.manage.msgUserDataSaveSuccess'));
  }
}

async function handleDeleteAccount() {
  dialog.warning({
    title: $t('general.warning'),
    content: $t('account.manage.msgDeleteAccountWarning'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    autoFocus: false,
    closable: false,
    positiveButtonProps: { ...dialogProps.positiveButtonProps, type: 'error' },
    negativeButtonProps: { ...dialogProps.negativeButtonProps, type: 'success' },
    onPositiveClick: async () => {
      loading.value = true;
      const { error } = await DELETE('/users/me', {});
      if (!error) {
        await auth.logout();
      }
      loading.value = false;
    },
  });
}
</script>

<template>
  <icon-heading level="1" :icon="ManageAccountIcon">
    {{ $t('account.manage.heading', { username: auth.user?.username }) }}
    <help-button-widget help-key="accountManageView" />
  </icon-heading>

  <div class="content-block">
    <h2>{{ $t('account.manage.headingChangeUserData') }}</h2>
    <n-form
      ref="userDataFormRef"
      :model="userDataFormModel"
      :rules="accountFormRules"
      :disabled="loading"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <n-form-item path="username" :label="$t('models.user.username')">
        <n-input
          v-model:value="userDataFormModel.username"
          type="text"
          :placeholder="$t('models.user.username')"
          @keydown.enter.prevent
        />
      </n-form-item>
      <n-form-item path="name" :label="$t('models.user.name')">
        <n-input
          v-model:value="userDataFormModel.name"
          type="text"
          :placeholder="$t('models.user.name')"
          @keydown.enter.prevent
        />
      </n-form-item>
      <n-form-item path="affiliation" :label="$t('models.user.affiliation')">
        <n-input
          v-model:value="userDataFormModel.affiliation"
          type="text"
          :placeholder="$t('models.user.affiliation')"
        />
      </n-form-item>
      <n-form-item path="avatarUrl" :label="$t('models.user.avatarUrl')">
        <n-input
          v-model:value="userDataFormModel.avatarUrl"
          type="text"
          :placeholder="$t('models.user.avatarUrl')"
        />
        <user-avatar
          :avatar-url="auth.user?.avatarUrl || undefined"
          :size="32"
          :fallback-icon="NoImageIcon"
          style="margin-left: var(--content-gap)"
        />
      </n-form-item>
      <n-form-item path="bio" :label="$t('models.user.bio')">
        <n-input
          v-model:value="userDataFormModel.bio"
          type="textarea"
          :maxlength="2000"
          :placeholder="$t('models.user.bio')"
        />
      </n-form-item>
    </n-form>
    <button-shelf top-gap>
      <n-button
        secondary
        :loading="loading"
        :disabled="loading || !userDataModelChanged"
        @click="() => (userDataFormModel = initialUserDataModel())"
      >
        {{ $t('general.resetAction') }}
      </n-button>
      <n-button
        type="primary"
        :loading="loading"
        :disabled="loading || !userDataModelChanged"
        @click="handleUserDataSave"
      >
        {{ $t('general.saveAction') }}
      </n-button>
    </button-shelf>
  </div>

  <div class="content-block">
    <h2>{{ $t('models.user.email') }}</h2>
    <n-form
      ref="emailFormRef"
      :model="emailFormModel"
      :rules="accountFormRules"
      :disabled="loading"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <n-form-item path="email" :label="$t('models.user.email')">
        <n-input
          v-model:value="emailFormModel.email"
          type="text"
          :placeholder="$t('models.user.email')"
          @keydown.enter.prevent
        />
      </n-form-item>
    </n-form>
    <button-shelf top-gap>
      <n-button
        secondary
        :loading="loading"
        :disabled="loading || !emailModelChanged"
        @click="() => (emailFormModel = initialEmailModel())"
      >
        {{ $t('general.resetAction') }}
      </n-button>
      <n-button
        type="primary"
        :loading="loading"
        :disabled="loading || !emailModelChanged"
        @click="handleEmailSave"
      >
        {{ $t('general.saveAction') }}
      </n-button>
    </button-shelf>

    <h2>{{ $t('models.user.password') }}</h2>
    <n-form
      ref="passwordFormRef"
      :model="passwordFormModel"
      :rules="accountFormRules"
      :disabled="loading"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <n-form-item path="password" :label="$t('models.user.password')">
        <n-input
          v-model:value="passwordFormModel.password"
          type="password"
          :placeholder="$t('models.user.password')"
          @input="handlePasswordInput"
          @keydown.enter.prevent
        />
      </n-form-item>
      <n-form-item
        ref="rPasswordFormItemRef"
        first
        path="passwordRepeat"
        :rule="accountFormRules.passwordRepeat.concat([passwordRepeatMatchRule])"
        :label="$t('register.repeatPassword')"
      >
        <n-input
          v-model:value="passwordFormModel.passwordRepeat"
          type="password"
          :disabled="!passwordFormModel.password || loading"
          :placeholder="$t('register.repeatPassword')"
          @keydown.enter.prevent
        />
      </n-form-item>
    </n-form>
    <button-shelf top-gap>
      <n-button
        secondary
        :loading="loading"
        :disabled="loading || !passwordModelChanged"
        @click="() => (passwordFormModel = initialPasswordModel())"
      >
        {{ $t('general.resetAction') }}
      </n-button>
      <n-button
        type="primary"
        :loading="loading"
        :disabled="loading || !passwordModelChanged"
        @click="handlePasswordSave"
      >
        {{ $t('general.saveAction') }}
      </n-button>
    </button-shelf>
  </div>

  <div class="content-block">
    <h2>
      {{ $t('account.manage.headingChangePublicFields') }}
      <help-button-widget help-key="accountManagePublicFields" />
    </h2>
    <n-form
      ref="publicFieldsFormRef"
      :model="publicFieldsFormModel"
      :show-label="false"
      :disabled="loading"
      require-mark-placement="right-hanging"
    >
      <n-space vertical>
        <labelled-switch
          :value="true"
          disabled
          :focusable="false"
          :label="$t('models.user.username')"
        />
        <template v-for="(_, field) in publicFieldsFormModel" :key="field">
          <labelled-switch
            v-model:value="publicFieldsFormModel[field]"
            :label="$t(`models.user.${field}`)"
            :disabled="loading"
          />
        </template>
      </n-space>
    </n-form>
    <button-shelf top-gap>
      <n-button
        secondary
        :loading="loading"
        :disabled="loading || !publicFieldsModelChanged"
        @click="() => (publicFieldsFormModel = initialPublicFieldsModel())"
      >
        {{ $t('general.resetAction') }}
      </n-button>
      <n-button
        type="primary"
        :loading="loading"
        :disabled="loading || !publicFieldsModelChanged"
        @click="handlepublicFieldsSave"
      >
        {{ $t('general.saveAction') }}
      </n-button>
    </button-shelf>
  </div>

  <div class="content-block">
    <h2>
      {{ $t('account.manage.headingDeleteAccount') }}
    </h2>
    <n-form-item :label="$t('models.user.username')" required>
      <n-input
        v-model:value="deleteAccountSafetyInput"
        type="text"
        :placeholder="
          $t('account.manage.phDeleteAccountSafetyInput', { username: auth.user?.username })
        "
        :disabled="loading"
        @keydown.enter.prevent
      />
    </n-form-item>
    <button-shelf top-gap>
      <n-button
        type="error"
        :focusable="false"
        :disabled="loading || deleteAccountSafetyInput !== auth.user?.username"
        @click="handleDeleteAccount"
      >
        {{ $t('account.manage.headingDeleteAccount') }}
      </n-button>
    </button-shelf>
  </div>
</template>

<style scoped>
.account-mgmt-grid .content-block {
  margin: 0;
}
</style>
