<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';
import {
  type FormInst,
  type FormItemInst,
  type FormItemRule,
  type FormRules,
  NForm,
  NFormItem,
  NInput,
  NButton,
  NSpace,
} from 'naive-ui';
import type { UserCreate } from '@/openapi';
import { useApi } from '@/api';
import { useMessages } from '@/messages';
import { usePlatformData } from '@/platformData';
import { useAuthStore } from '@/stores';

const auth = useAuthStore();
const { message } = useMessages();
const { pfData } = usePlatformData();
const { authApi } = useApi();
const { t } = useI18n({ useScope: 'global' });

const initialFormModel = () => ({
  email: null,
  username: null,
  password: null,
  passwordRepeat: null,
  firstName: null,
  lastName: null,
  affiliation: null,
});

const formModel = ref<Record<string, string | null>>(initialFormModel());
const formRef = ref<FormInst | null>(null);
const rPasswordFormItemRef = ref<FormItemInst | null>(null);
const firstInputRef = ref<HTMLInputElement | null>(null);
const loading = ref(false);

const formRules: FormRules = {
  email: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.user.email') }),
      // trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) => /^.+@.+\.\w+$/.test(value),
      message: () => t('register.rulesFeedback.emailInvalid'),
      // trigger: 'blur',
    },
  ],
  username: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.user.username') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 4 && value.length <= 16,
      message: () => t('forms.rulesFeedback.minMaxChars', { min: 4, max: 16 }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) => !!value && /^[a-zA-Z0-9\-_]*$/.test(value),
      message: () => t('register.rulesFeedback.usernameChars'),
      trigger: 'blur',
    },
  ],
  password: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.user.password') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) => !!value && value.length >= 8,
      message: () => t('forms.rulesFeedback.minChars', { min: 8 }),
      trigger: ['input', 'blur'],
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/.test(value),
      message: () => t('register.rulesFeedback.passwordChars'),
      trigger: ['input', 'blur'],
    },
  ],
  passwordRepeat: [
    {
      required: true,
      message: () => t('register.rulesFeedback.passwordRepReq'),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && !!formModel.value.password && value === formModel.value.password,
      message: () => t('register.rulesFeedback.passwordRepNoMatch'),
      trigger: ['input', 'blur', 'password-input'],
    },
  ],
  firstName: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.user.firstName') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 32,
      message: () => t('forms.rulesFeedback.minMaxChars', { min: 1, max: 32 }),
      trigger: 'blur',
    },
  ],
  lastName: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.user.lastName') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 1 && value.length <= 32,
      message: () => t('forms.rulesFeedback.minMaxChars', { min: 1, max: 32 }),
      trigger: 'blur',
    },
  ],
  affiliation: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.user.affiliation') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) =>
        !!value && value.length >= 4 && value.length <= 64,
      message: () => t('forms.rulesFeedback.minMaxChars', { min: 4, max: 64 }),
      trigger: 'blur',
    },
  ],
};

function handlePasswordInput() {
  if (formModel.value.reenteredPassword) {
    rPasswordFormItemRef.value?.validate({ trigger: 'password-input' });
  }
}

function registerUser() {
  authApi
    .registerRegister({ userCreate: formModel.value as unknown as UserCreate })
    .then(() => {
      const activationNeeded = !pfData.value?.security?.usersActiveByDefault;
      const activationHint = activationNeeded
        ? t('register.activationNeededHint')
        : t('register.activationNotNeededHint');
      message.success(`${t('register.success')} ${activationHint}`, activationNeeded ? 20 : 5);
      switchToLogin();
    })
    .catch((e) => {
      /**
       * Unfortunately, the errors returned by the endpoints generated by
       * FastAPI-Users have a weird custom model that we have to handle here...
       */
      if (e.response) {
        const data = e.response.data;
        if (data.detail === 'REGISTER_USER_ALREADY_EXISTS') {
          message.error(t('register.errors.emailAlreadyRegistered'));
        } else if (data.detail === 'REGISTER_USERNAME_ALREADY_EXISTS') {
          message.error(t('register.errors.usernameAlreadyRegistered'));
        } else if (data.detail.code === 'REGISTER_INVALID_PASSWORD') {
          message.error(t('register.errors.weakPassword'));
        } else if (e.response.status === 403) {
          message.error(t('errors.csrf'));
        } else {
          message.error(t('errors.unexpected'));
        }
      }
      loading.value = false;
    });
}

function handleRegisterClick(e: MouseEvent | null = null) {
  e && e.preventDefault();
  loading.value = true;
  formRef.value
    ?.validate((errors) => {
      !errors && registerUser();
    })
    .catch(() => {
      message.error(t('errors.followFormRules'));
      loading.value = false;
    });
}

function resetForm() {
  loading.value = false;
  formModel.value = initialFormModel();
  formRef.value?.restoreValidation();
}

function switchToLogin() {
  resetForm();
  auth.showLoginModal(undefined, { name: 'accountProfile' });
}

onMounted(() => {
  nextTick(() => {
    firstInputRef.value?.focus();
  });
});
</script>

<template>
  <h2 style="text-align: center">{{ $t('register.heading') }}</h2>
  <div class="form-container">
    <div class="content-block">
      <n-form
        ref="formRef"
        :model="formModel"
        :rules="formRules"
        label-placement="top"
        label-width="auto"
        require-mark-placement="right-hanging"
      >
        <n-form-item path="email" :label="$t('models.user.email')">
          <n-input
            v-model:value="formModel.email"
            type="text"
            :placeholder="$t('models.user.email')"
            @keydown.enter.prevent
            ref="firstInputRef"
          />
        </n-form-item>
        <n-form-item path="username" :label="$t('models.user.username')">
          <n-input
            v-model:value="formModel.username"
            type="text"
            :placeholder="$t('models.user.username')"
            @keydown.enter.prevent
          />
        </n-form-item>
        <n-form-item path="password" :label="$t('models.user.password')">
          <n-input
            v-model:value="formModel.password"
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
          :label="$t('register.repeatPassword')"
        >
          <n-input
            v-model:value="formModel.passwordRepeat"
            type="password"
            :disabled="!formModel.password"
            :placeholder="$t('register.repeatPassword')"
            @keydown.enter.prevent
          />
        </n-form-item>
        <n-form-item path="firstName" :label="$t('models.user.firstName')">
          <n-input
            v-model:value="formModel.firstName"
            type="text"
            :placeholder="$t('models.user.firstName')"
            @keydown.enter.prevent
          />
        </n-form-item>
        <n-form-item path="lastName" :label="$t('models.user.lastName')">
          <n-input
            v-model:value="formModel.lastName"
            type="text"
            :placeholder="$t('models.user.lastName')"
            @keydown.enter.prevent
          />
        </n-form-item>
        <n-form-item path="affiliation" :label="$t('models.user.affiliation')">
          <n-input
            v-model:value="formModel.affiliation"
            type="text"
            :placeholder="$t('models.user.affiliation')"
            @keyup.enter="() => handleRegisterClick()"
          />
        </n-form-item>
      </n-form>

      <n-space vertical :size="12" style="margin-top: 1rem">
        <n-button
          block
          type="primary"
          @click="handleRegisterClick"
          :loading="loading"
          :disabled="loading"
        >
          {{ $t('register.register') }}
        </n-button>
        <n-button secondary block @click="switchToLogin">
          {{ $t('register.switchToLogin') }}
        </n-button>
      </n-space>
    </div>
  </div>
</template>
