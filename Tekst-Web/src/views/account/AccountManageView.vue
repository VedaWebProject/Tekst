<script setup lang="ts">
import { POST } from '@/api';
import { accountFormRules } from '@/formRules';
import { useMessages } from '@/messages';
import { usePlatformData } from '@/platformData';
import { useAuthStore } from '@/stores';
import type { FormInst, FormItemInst, FormItemRule } from 'naive-ui';
import {
  NCheckbox,
  NButton,
  NInput,
  NFormItem,
  NForm,
  NGrid,
  NGridItem,
  useDialog,
} from 'naive-ui';
import { ref } from 'vue';
import { $t } from '@/i18n';
import { useModelChanges } from '@/modelChanges';
import type { UserUpdate, UserUpdatePublicFields } from '@/api';
import { negativeButtonProps, positiveButtonProps } from '@/components/dialogButtonProps';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/typography/IconHeading.vue';
import ButtonFooter from '@/components/ButtonFooter.vue';

import ManageAccountsRound from '@vicons/material/ManageAccountsRound';

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
  firstName: auth.user?.firstName || null,
  lastName: auth.user?.lastName || null,
  affiliation: auth.user?.affiliation || null,
});

const initialPublicFieldsModel = () => ({
  firstName: auth.user?.publicFields?.includes('firstName') || false,
  lastName: auth.user?.publicFields?.includes('lastName') || false,
  affiliation: auth.user?.publicFields?.includes('affiliation') || false,
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
const firstInputRef = ref<HTMLInputElement | null>(null);
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
  try {
    await auth.updateUser(userUpdate);
    return true;
  } catch {
    /**
     * This will be either an app-level error (e.g. buggy validation, server down),
     * the provided email already exists (which we don't want to actively disclose)
     * or we got a 403 for a failed CSRF check.
     */
    message.error($t('errors.unexpected'));
    return false;
  } finally {
    loading.value = false;
  }
}

async function updateEmail() {
  if (!(await updateUser(getEmailModelChanges()))) return;
  resetEmailModelChanges();
  message.success($t('account.manage.msgEmailSaveSuccess'));
  if (pfData.value?.security?.closedMode === true) return;
  await auth.logout();
  const { error } = await POST('/auth/request-verify-token', {
    body: { email: emailFormModel.value.email || '' },
  });
  if (!error) {
    message.warning($t('account.manage.msgVerifyEmailWarning'), undefined, 20);
  } else {
    message.error($t('errors.unexpected'), error);
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
            positiveButtonProps,
            negativeButtonProps,
            autoFocus: false,
            closable: false,
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
          positiveButtonProps,
          negativeButtonProps,
          autoFocus: false,
          closable: false,
          onPositiveClick: async () => {
            await updateUser({ password: passwordFormModel.value.password || undefined });
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
      if (!validationErrors && (await updateUser(getUserDataModelChanges()))) {
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
    resetPublicFieldsModelChanges();
    message.success($t('account.manage.msgUserDataSaveSuccess'));
  }
}
</script>

<template>
  <IconHeading level="1" :icon="ManageAccountsRound">
    {{ $t('account.manage.heading', { username: auth.user?.username }) }}
    <HelpButtonWidget help-key="accountManageView" />
  </IconHeading>

  <n-grid class="account-mgmt-grid" cols="1 m:2" responsive="screen" x-gap="18px" y-gap="18px">
    <n-grid-item>
      <div class="content-block">
        <h2>{{ $t('models.user.email') }}</h2>
        <n-form
          ref="emailFormRef"
          :model="emailFormModel"
          :rules="accountFormRules"
          label-placement="top"
          label-width="auto"
          require-mark-placement="right-hanging"
        >
          <n-form-item path="email" :label="$t('models.user.email')">
            <n-input
              ref="firstInputRef"
              v-model:value="emailFormModel.email"
              type="text"
              :placeholder="$t('models.user.email')"
              :disabled="loading"
              @keydown.enter.prevent
            />
          </n-form-item>
        </n-form>
        <ButtonFooter>
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
        </ButtonFooter>

        <h2>{{ $t('models.user.password') }}</h2>
        <n-form
          ref="passwordFormRef"
          :model="passwordFormModel"
          :rules="accountFormRules"
          label-placement="top"
          label-width="auto"
          require-mark-placement="right-hanging"
        >
          <n-form-item path="password" :label="$t('models.user.password')">
            <n-input
              v-model:value="passwordFormModel.password"
              type="password"
              :placeholder="$t('models.user.password')"
              :disabled="loading"
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
        <ButtonFooter>
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
        </ButtonFooter>
      </div>
    </n-grid-item>

    <n-grid-item>
      <div class="content-block">
        <h2>{{ $t('account.manage.headingChangeUserData') }}</h2>
        <n-form
          ref="userDataFormRef"
          :model="userDataFormModel"
          :rules="accountFormRules"
          label-placement="top"
          label-width="auto"
          require-mark-placement="right-hanging"
        >
          <n-form-item path="username" :label="$t('models.user.username')">
            <n-input
              v-model:value="userDataFormModel.username"
              type="text"
              :placeholder="$t('models.user.username')"
              :disabled="loading"
              @keydown.enter.prevent
            />
          </n-form-item>
          <n-form-item path="firstName" :label="$t('models.user.firstName')">
            <n-input
              v-model:value="userDataFormModel.firstName"
              type="text"
              :placeholder="$t('models.user.firstName')"
              :disabled="loading"
              @keydown.enter.prevent
            />
          </n-form-item>
          <n-form-item path="lastName" :label="$t('models.user.lastName')">
            <n-input
              v-model:value="userDataFormModel.lastName"
              type="text"
              :placeholder="$t('models.user.lastName')"
              :disabled="loading"
              @keydown.enter.prevent
            />
          </n-form-item>
          <n-form-item path="affiliation" :label="$t('models.user.affiliation')">
            <n-input
              v-model:value="userDataFormModel.affiliation"
              type="text"
              :placeholder="$t('models.user.affiliation')"
              :disabled="loading"
            />
          </n-form-item>
        </n-form>
        <ButtonFooter>
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
        </ButtonFooter>
      </div>
    </n-grid-item>

    <n-grid-item>
      <div class="content-block">
        <h2>
          {{ $t('account.manage.headingChangePublicFields') }}
          <HelpButtonWidget help-key="accountManagePublicFields" />
        </h2>
        <n-form
          ref="publicFieldsFormRef"
          :model="publicFieldsFormModel"
          :show-label="false"
          require-mark-placement="right-hanging"
        >
          <n-form-item>
            <n-checkbox checked disabled aria-readonly :focusable="false">
              {{ $t(`models.user.username`) }}
            </n-checkbox>
          </n-form-item>
          <n-form-item v-for="(_, field) in publicFieldsFormModel" :key="field" :path="field">
            <n-checkbox v-model:checked="publicFieldsFormModel[field]" :disabled="loading">
              {{ $t(`models.user.${field}`) }}
            </n-checkbox>
          </n-form-item>
        </n-form>
        <ButtonFooter>
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
        </ButtonFooter>
      </div>
    </n-grid-item>
  </n-grid>
</template>

<style scoped>
.account-mgmt-grid .content-block {
  margin: 0;
}
</style>
