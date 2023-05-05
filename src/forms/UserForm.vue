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
} from 'naive-ui';

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

const formRef = ref<FormInst | null>(null);
const formModel = ref<Record<string, string | null>>(initialFormModel());
const rPasswordFormItemRef = ref<FormItemInst | null>(null);
const firstInputRef = ref<HTMLInputElement | null>(null);

const formRules: FormRules = {
  email: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.user.email') }),
      trigger: 'blur',
    },
    {
      validator: (rule: FormItemRule, value: string) => /^.+@.+\.\w+$/.test(value),
      message: () => t('register.rulesFeedback.emailInvalid'),
      trigger: 'blur',
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

function reset() {
  formModel.value = initialFormModel();
  formRef.value?.restoreValidation();
}

onMounted(() => {
  nextTick(() => {
    firstInputRef.value?.focus();
  });
});

defineExpose({ formRef, formModel, reset });
</script>

<template>
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
        @keyup.enter="$emit('submit')"
      />
    </n-form-item>
  </n-form>
</template>
