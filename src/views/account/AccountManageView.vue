<script setup lang="ts">
import { useFormRules } from '@/formRules';
import { useMessages } from '@/messages';
import type { UserUpdate } from '@/openapi';
import { useAuthStore } from '@/stores';
import type { FormInst, FormItemInst, FormItemRule } from 'naive-ui';
import { NButton, NSpace, NInput, NFormItem, NForm, NGrid, NGridItem, useDialog } from 'naive-ui';
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';

const dialog = useDialog();
const auth = useAuthStore();
const { message } = useMessages();
const { t } = useI18n({ useScope: 'global' });

const initialEmailFormModel = () => ({
  email: auth.user?.email || null,
});

const initialPasswordFormModel = () => ({
  password: '',
  passwordRepeat: '',
});

const initialUserDataFormModel = () => ({
  username: auth.user?.username || null,
  firstName: auth.user?.firstName || null,
  lastName: auth.user?.lastName || null,
  affiliation: auth.user?.affiliation || null,
});

const formRules = useFormRules();

const emailFormRef = ref<FormInst | null>(null);
const emailFormModel = ref<Record<string, string | null>>(initialEmailFormModel());
const emailModelChanged = computed(() =>
  modelChanged(passwordFormModel.value, initialPasswordFormModel())
);

const passwordFormRef = ref<FormInst | null>(null);
const passwordFormModel = ref<Record<string, string | null>>(initialPasswordFormModel());
const passwordModelChanged = computed(() =>
  modelChanged(passwordFormModel.value, initialPasswordFormModel())
);

const userDataFormRef = ref<FormInst | null>(null);
const userDataFormModel = ref<Record<string, string | null>>(initialUserDataFormModel());
const userDataModelChanged = computed(() =>
  modelChanged(userDataFormModel.value, initialUserDataFormModel())
);

const rPasswordFormItemRef = ref<FormItemInst | null>(null);
const firstInputRef = ref<HTMLInputElement | null>(null);
const loading = ref(false);

const passwordRepeatMatchRule = {
  validator: (rule: FormItemRule, value: string) =>
    !!value && !!passwordFormModel.value.password && value === passwordFormModel.value.password,
  message: () => t('register.rulesFeedback.passwordRepNoMatch'),
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
     * This will be either an app-level error (e.g. buggy validation, server down, 401)
     * or the provided email already exists, which we don't want to actively disclose.
     */
    message.error(t('errors.unexpected'));
    return false;
  } finally {
    loading.value = false;
  }
}

function keepChanged(
  changed: Record<string, string | null>,
  original: Record<string, string | null>
) {
  return Object.keys(changed).reduce((prev, curr) => {
    if (changed[curr] !== original[curr]) prev[curr] = changed[curr];
    return prev;
  }, {} as Record<string, string | null>);
}

function modelChanged(
  changed: Record<string, string | null>,
  original: Record<string, string | null>
) {
  for (const key in original) {
    if (changed[key] !== original[key]) {
      return true;
    }
  }
  return false;
}

function handleEmailSave() {
  emailFormRef.value
    ?.validate(async (errors) => {
      !errors &&
        dialog.warning({
          title: t('general.warning'),
          content: t('account.manage.msgEmailChangeWarning'),
          positiveText: t('general.saveAction'),
          negativeText: t('general.cancelAction'),
          style: 'font-weight: var(--app-ui-font-weight-light)',
          onPositiveClick: async () => {
            await updateUser(keepChanged(emailFormModel.value, initialEmailFormModel()));
            message.success(t('account.manage.msgEmailSaveSuccess'));
            message.warning(t('account.manage.msgVerifyEmailWarning'), 20);
            await auth.logout();
            auth.showLoginModal(
              t('account.manage.msgVerifyEmailWarning'),
              { name: 'accountProfile' },
              false
            );
          },
        });
    })
    .catch(() => {
      message.error(t('errors.followFormRules'));
    });
}

async function handlePasswordSave() {
  passwordFormRef.value
    ?.validate(async (errors) => {
      !errors &&
        dialog.warning({
          title: t('general.warning'),
          content: t('account.manage.msgPasswordChangeWarning'),
          positiveText: t('general.saveAction'),
          negativeText: t('general.cancelAction'),
          style: 'font-weight: var(--app-ui-font-weight-light)',
          onPositiveClick: async () => {
            await updateUser({ password: passwordFormModel.value.password || undefined });
            message.success(t('account.manage.msgPasswordSaveSuccess'));
            await auth.logout();
            auth.showLoginModal(undefined, { name: 'accountProfile' }, false);
          },
        });
    })
    .catch(() => {
      message.error(t('errors.followFormRules'));
    });
}

async function handleUserDataSave() {
  userDataFormRef.value
    ?.validate(async (errors) => {
      if (!errors) {
        await updateUser(keepChanged(userDataFormModel.value, initialUserDataFormModel()));
        message.success(t('account.manage.msgUserDataSaveSuccess'));
      }
    })
    .catch(() => {
      message.error(t('errors.followFormRules'));
    });
}
</script>

<template>
  <h1>{{ $t('account.manage.heading') }}</h1>

  <n-grid cols="1 m:2" responsive="screen" x-gap="20px">
    <n-grid-item>
      <div class="content-block">
        <h2>{{ t('models.user.email') }}</h2>
        <n-form
          ref="emailFormRef"
          :model="emailFormModel"
          :rules="formRules"
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
              :disabled="loading"
              ref="firstInputRef"
            />
          </n-form-item>
        </n-form>
        <n-space :size="12" justify="end">
          <n-button
            block
            type="primary"
            @click="handleEmailSave"
            :loading="loading"
            :disabled="loading || !emailModelChanged"
          >
            {{ $t('general.saveAction') }}
          </n-button>
        </n-space>

        <h2>{{ t('models.user.password') }}</h2>
        <n-form
          ref="passwordFormRef"
          :model="passwordFormModel"
          :rules="formRules"
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
              :disabled="loading"
            />
          </n-form-item>
          <n-form-item
            ref="rPasswordFormItemRef"
            first
            path="passwordRepeat"
            :rule="formRules.passwordRepeat.concat([passwordRepeatMatchRule])"
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
        <n-space :size="12" justify="end">
          <n-button
            block
            type="primary"
            @click="handlePasswordSave"
            :loading="loading"
            :disabled="loading || !passwordModelChanged"
          >
            {{ $t('general.saveAction') }}
          </n-button>
        </n-space>
      </div>
    </n-grid-item>

    <n-grid-item>
      <div class="content-block">
        <h2>{{ t('account.manage.headingChangeUserData') }}</h2>
        <n-form
          ref="userDataFormRef"
          :model="userDataFormModel"
          :rules="formRules"
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
              :disabled="loading"
            />
          </n-form-item>
          <n-form-item path="firstName" :label="$t('models.user.firstName')">
            <n-input
              v-model:value="userDataFormModel.firstName"
              type="text"
              :placeholder="$t('models.user.firstName')"
              @keydown.enter.prevent
              :disabled="loading"
            />
          </n-form-item>
          <n-form-item path="lastName" :label="$t('models.user.lastName')">
            <n-input
              v-model:value="userDataFormModel.lastName"
              type="text"
              :placeholder="$t('models.user.lastName')"
              @keydown.enter.prevent
              :disabled="loading"
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
        <n-space :size="12" justify="end">
          <n-button
            block
            type="primary"
            @click="handleUserDataSave"
            :loading="loading"
            :disabled="loading || !userDataModelChanged"
          >
            {{ $t('general.saveAction') }}
          </n-button>
        </n-space>
      </div>
    </n-grid-item>
  </n-grid>
</template>
