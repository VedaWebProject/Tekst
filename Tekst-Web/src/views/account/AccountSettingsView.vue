<script setup lang="ts">
import { DELETE, POST } from '@/api';
import { accountFormRules } from '@/forms/formRules';
import { useMessages } from '@/composables/messages';
import { usePlatformData } from '@/composables/platformData';
import { useAuthStore } from '@/stores';
import type { FormInst, FormItemInst, FormItemRule } from 'naive-ui';
import { NButton, NInput, NFormItem, NForm, useDialog, NFlex } from 'naive-ui';
import { ref } from 'vue';
import { $t } from '@/i18n';
import { useModelChanges } from '@/composables/modelChanges';
import type {
  UserUpdate,
  UserUpdatePublicFields,
  UserUpdateAdminNotificationTriggers,
  UserUpdateUserNotificationTriggers,
} from '@/api';
import { dialogProps } from '@/common';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import UserAvatar from '@/components/user/UserAvatar.vue';
import { ManageAccountIcon, NoImageIcon } from '@/icons';
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import { checkUrl } from '@/utils';

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

const initialUserNotificationTriggersModel = () => ({
  resourceProposed: !!auth.user?.userNotificationTriggers.includes('resourceProposed'),
  resourcePublished: !!auth.user?.userNotificationTriggers.includes('resourcePublished'),
  messageReceived: !!auth.user?.userNotificationTriggers.includes('messageReceived'),
  newCorrection: !!auth.user?.userNotificationTriggers.includes('newCorrection'),
});

const initialAdminNotificationTriggersModel = () => ({
  userAwaitsActivation: !!auth.user?.adminNotificationTriggers.includes('userAwaitsActivation'),
  newCorrection: !!auth.user?.adminNotificationTriggers.includes('newCorrection'),
});

const initialPublicFieldsModel = () => ({
  name: !!auth.user?.publicFields.includes('name'),
  affiliation: !!auth.user?.publicFields.includes('affiliation'),
  bio: !!auth.user?.publicFields.includes('bio'),
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

const userNotificationTriggersFormRef = ref<FormInst | null>(null);
const userNotificationTriggersFormModel = ref<Record<string, boolean>>(
  initialUserNotificationTriggersModel()
);
const {
  changed: userNotificationTriggersModelChanged,
  reset: resetUserNotificationTriggersModelChanges,
} = useModelChanges(userNotificationTriggersFormModel);

const adminNotificationTriggersFormRef = ref<FormInst | null>(null);
const adminNotificationTriggersFormModel = ref<Record<string, boolean>>(
  initialAdminNotificationTriggersModel()
);
const {
  changed: adminNotificationTriggersModelChanged,
  reset: resetAdminNotificationTriggersModelChanges,
} = useModelChanges(adminNotificationTriggersFormModel);

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
  message.success($t('account.settings.msgEmailSaveSuccess'));
  if (pfData.value?.security.closedMode === true) return;
  await auth.logout();
  const { error } = await POST('/auth/request-verify-token', {
    body: { email: emailFormModel.value.email || '' },
  });
  if (!error) {
    message.warning($t('account.settings.msgVerifyEmailWarning'), undefined, 20);
  }
  auth.showLoginModal(
    $t('account.settings.msgVerifyEmailWarning'),
    { name: 'accountProfile' },
    false
  );
}

function handleEmailSave() {
  emailFormRef.value
    ?.validate(async (errors) => {
      if (!errors) {
        if (pfData.value?.security.closedMode) {
          updateEmail();
        } else {
          dialog.warning({
            title: $t('general.warning'),
            content: $t('account.settings.msgEmailChangeWarning'),
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
      if (errors) return;
      dialog.warning({
        title: $t('general.warning'),
        content: $t('account.settings.msgPasswordChangeWarning'),
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
          message.success($t('account.settings.msgPasswordSaveSuccess'));
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
        message.success($t('account.settings.msgUserDataSaveSuccess'));
      }
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    });
}

async function handleUserNotificationTriggersSave() {
  if (
    await updateUser({
      userNotificationTriggers: Object.keys(userNotificationTriggersFormModel.value).filter(
        (k) => userNotificationTriggersFormModel.value[k]
      ) as UserUpdateUserNotificationTriggers,
    })
  ) {
    userNotificationTriggersFormModel.value = initialUserNotificationTriggersModel();
    resetUserNotificationTriggersModelChanges();
    message.success($t('account.settings.userNotificationTriggers.msgSaveSuccess'));
  }
}

async function handleAdminNotificationTriggersSave() {
  if (
    await updateUser({
      adminNotificationTriggers: Object.keys(adminNotificationTriggersFormModel.value).filter(
        (k) => adminNotificationTriggersFormModel.value[k]
      ) as UserUpdateAdminNotificationTriggers,
    })
  ) {
    adminNotificationTriggersFormModel.value = initialAdminNotificationTriggersModel();
    resetAdminNotificationTriggersModelChanges();
    message.success($t('account.settings.adminNotificationTriggers.msgSaveSuccess'));
  }
}

async function handlePublicFieldsSave() {
  if (
    await updateUser({
      publicFields: Object.keys(publicFieldsFormModel.value).filter(
        (k) => publicFieldsFormModel.value[k]
      ) as UserUpdatePublicFields,
    })
  ) {
    publicFieldsFormModel.value = initialPublicFieldsModel();
    resetPublicFieldsModelChanges();
    message.success($t('account.settings.msgUserDataSaveSuccess'));
  }
}

async function handleDeleteAccount() {
  dialog.warning({
    title: $t('general.warning'),
    content: $t('account.settings.msgDeleteAccountWarning'),
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

async function checkUrlInput(input: HTMLInputElement) {
  const url = input.value;
  if (url && !(await checkUrl(url))) {
    message.warning($t('contents.warnUrlInvalid', { url }), undefined, 3);
    input.classList.add('invalid-url');
  } else {
    input.classList.remove('invalid-url');
  }
}
</script>

<template>
  <icon-heading level="1" :icon="ManageAccountIcon">
    {{ $t('account.settings.heading') }}
    <help-button-widget help-key="accountSettingsView" />
  </icon-heading>

  <!-- GENERAL USER DATA -->
  <div class="content-block">
    <h2>{{ $t('account.settings.headingChangeUserData') }}</h2>
    <n-form
      ref="userDataFormRef"
      :model="userDataFormModel"
      :rules="accountFormRules"
      :disabled="loading"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <!-- USERNAME -->
      <n-form-item path="username" :label="$t('models.user.username')">
        <n-input
          v-model:value="userDataFormModel.username"
          type="text"
          :placeholder="$t('models.user.username')"
          @keydown.enter.prevent
        />
      </n-form-item>
      <!-- NAME -->
      <n-form-item path="name" :label="$t('models.user.name')">
        <n-input
          v-model:value="userDataFormModel.name"
          type="text"
          :placeholder="$t('models.user.name')"
          @keydown.enter.prevent
        />
      </n-form-item>
      <!-- AFFILIATION -->
      <n-form-item path="affiliation" :label="$t('models.user.affiliation')">
        <n-input
          v-model:value="userDataFormModel.affiliation"
          type="text"
          :placeholder="$t('models.user.affiliation')"
        />
      </n-form-item>
      <!-- AVATAR URL -->
      <n-form-item path="avatarUrl" :label="$t('models.user.avatarUrl')">
        <n-input
          v-model:value="userDataFormModel.avatarUrl"
          :placeholder="$t('models.user.avatarUrl')"
          @input-blur="checkUrlInput($event.target as HTMLInputElement)"
        />
        <user-avatar
          :avatar-url="userDataFormModel.avatarUrl || undefined"
          :size="32"
          :fallback-icon="NoImageIcon"
          class="ml-md"
        />
      </n-form-item>
      <!-- BIO -->
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

  <!-- EMAIL AND PASSWORD -->
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
          show-password-on="mousedown"
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
          show-password-on="mousedown"
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

  <!-- PUBLIC PROFILE DATA -->
  <div class="content-block">
    <icon-heading level="2">
      {{ $t('account.settings.headingChangePublicFields') }}
      <help-button-widget help-key="accountSettingsPublicFields" />
    </icon-heading>
    <n-form
      ref="publicFieldsFormRef"
      :model="publicFieldsFormModel"
      :show-label="false"
      :disabled="loading"
      require-mark-placement="right-hanging"
    >
      <n-flex vertical>
        <labelled-switch
          :model-value="true"
          disabled
          :focusable="false"
          :label="$t('models.user.username')"
        />
        <template v-for="(_, field) in publicFieldsFormModel" :key="field">
          <labelled-switch
            v-model="publicFieldsFormModel[field]"
            :label="$t(`models.user.${field}`)"
            :disabled="loading"
          />
        </template>
      </n-flex>
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
        @click="handlePublicFieldsSave"
      >
        {{ $t('general.saveAction') }}
      </n-button>
    </button-shelf>
  </div>

  <!-- USER NOTIFICATION TRIGGERS -->
  <div class="content-block">
    <h2>
      {{ $t('account.settings.userNotificationTriggers.heading') }}
    </h2>
    <p>{{ $t('account.settings.notifyMe') }}</p>
    <n-form
      ref="userNotificationTriggersFormRef"
      :model="userNotificationTriggersFormModel"
      :show-label="false"
      :disabled="loading"
      require-mark-placement="right-hanging"
    >
      <n-flex vertical>
        <template v-for="(_, field) in userNotificationTriggersFormModel" :key="field">
          <labelled-switch
            v-model="userNotificationTriggersFormModel[field]"
            :label="$t(`account.settings.userNotificationTriggers.${field}`)"
            :disabled="loading"
          />
        </template>
      </n-flex>
    </n-form>
    <button-shelf top-gap>
      <n-button
        secondary
        :loading="loading"
        :disabled="loading || !userNotificationTriggersModelChanged"
        @click="() => (userNotificationTriggersFormModel = initialUserNotificationTriggersModel())"
      >
        {{ $t('general.resetAction') }}
      </n-button>
      <n-button
        type="primary"
        :loading="loading"
        :disabled="loading || !userNotificationTriggersModelChanged"
        @click="handleUserNotificationTriggersSave"
      >
        {{ $t('general.saveAction') }}
      </n-button>
    </button-shelf>
  </div>

  <!-- ADMIN NOTIFICATION TRIGGERS -->
  <div v-if="auth.user?.isSuperuser" class="content-block">
    <h2>
      {{ $t('account.settings.adminNotificationTriggers.heading') }}
    </h2>
    <p>{{ $t('account.settings.notifyMe') }}</p>
    <n-form
      ref="adminNotificationTriggersFormRef"
      :model="adminNotificationTriggersFormModel"
      :show-label="false"
      :disabled="loading"
      require-mark-placement="right-hanging"
    >
      <n-flex vertical>
        <template v-for="(_, field) in adminNotificationTriggersFormModel" :key="field">
          <labelled-switch
            v-model="adminNotificationTriggersFormModel[field]"
            :label="$t(`account.settings.adminNotificationTriggers.${field}`)"
            :disabled="loading"
          />
        </template>
      </n-flex>
    </n-form>
    <button-shelf top-gap>
      <n-button
        secondary
        :loading="loading"
        :disabled="loading || !adminNotificationTriggersModelChanged"
        @click="
          () => (adminNotificationTriggersFormModel = initialAdminNotificationTriggersModel())
        "
      >
        {{ $t('general.resetAction') }}
      </n-button>
      <n-button
        type="primary"
        :loading="loading"
        :disabled="loading || !adminNotificationTriggersModelChanged"
        @click="handleAdminNotificationTriggersSave"
      >
        {{ $t('general.saveAction') }}
      </n-button>
    </button-shelf>
  </div>

  <!-- DELETE ACCOUNT -->
  <div class="content-block">
    <h2>
      {{ $t('account.settings.headingDeleteAccount') }}
    </h2>
    <n-form-item :label="$t('models.user.username')" required>
      <n-input
        v-model:value="deleteAccountSafetyInput"
        type="text"
        :placeholder="
          $t('account.settings.phDeleteAccountSafetyInput', { username: auth.user?.username })
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
        {{ $t('account.settings.headingDeleteAccount') }}
      </n-button>
    </button-shelf>
  </div>
</template>

<style scoped>
.account-mgmt-grid .content-block {
  margin: 0;
}
</style>
