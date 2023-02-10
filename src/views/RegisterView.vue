<script setup lang="ts">
import { ref } from 'vue';
import { useMessagesStore, useUiDataStore } from '@/stores';
import {
  type FormInst,
  type FormItemInst,
  type FormItemRule,
  type FormValidationError,
  type FormRules,
  NForm,
  NFormItem,
  NInput,
  NRow,
  NCol,
  NButton,
} from 'naive-ui';
import { AuthApi } from 'textrig-ts-client';
import { UserCreateFromJSON } from 'textrig-ts-client';

const ui = useUiDataStore();
const authApi = new AuthApi();
// const user = ref<UserCreate>(UserCreateFromJSON({}));

const formModel = ref<Record<string, string | null>>({
  email: null,
  password: null,
  passwordRepeat: null,
  firstName: null,
  lastName: null,
});

const formRef = ref<FormInst | null>(null);
const rPasswordFormItemRef = ref<FormItemInst | null>(null);
const messages = useMessagesStore();

function validateEmail(rule: FormItemRule, value: string): boolean {
  return /^.+@.+\.\w+$/.test(value);
}

function validatePasswordLength(rule: FormItemRule, value: string): boolean {
  return !!value && value.length >= 8;
}

function validatePasswordChars(rule: FormItemRule, value: string): boolean {
  return !!value && /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/.test(value);
}

function validatePasswordsMatch(rule: FormItemRule, value: string): boolean {
  return !!value && !!formModel.value.password && value === formModel.value.password;
}

const rules: FormRules = {
  email: [
    {
      required: true,
      message: 'Email is required',
      trigger: 'blur',
    },
    {
      validator: validateEmail,
      message: 'Email is too obviously invalid',
      trigger: 'blur',
    },
  ],
  password: [
    {
      required: true,
      message: 'Password is required',
      trigger: 'blur',
    },
    {
      validator: validatePasswordLength,
      message: 'Password must be at least 8 characters long',
      trigger: ['input', 'blur'],
    },
    {
      validator: validatePasswordChars,
      message: 'Password must contain at least one of each: a-z, A-Z and 0-9',
      trigger: ['input', 'blur'],
    },
  ],
  passwordRepeat: [
    {
      required: true,
      message: 'Repeated password is required',
      trigger: 'blur',
    },
    {
      validator: validatePasswordsMatch,
      message: "Passwords don't match",
      trigger: ['input', 'blur', 'password-input'],
    },
  ],
};

function handlePasswordInput() {
  if (formModel.value.reenteredPassword) {
    rPasswordFormItemRef.value?.validate({ trigger: 'password-input' });
  }
}

function handleRegisterButtonClick(e: MouseEvent) {
  e.preventDefault();
  formRef.value?.validate((errors: Array<FormValidationError> | undefined) => {
    if (!errors) {
      authApi.registerRegister({ userCreate: UserCreateFromJSON(formModel.value) });
    } else {
      errors.forEach((error) => error.forEach((part) => messages.error(part.message)));
    }
  });
}
</script>

<template>
  <h1>{{ ui.get('platform.title') }} Registration</h1>

  <n-form ref="formRef" :model="formModel" :rules="rules" label-placement="left" label-width="auto">
    <n-form-item path="email" label="Email">
      <n-input
        v-model:value="formModel.email"
        type="text"
        placeholder="..."
        @keydown.enter.prevent
      />
    </n-form-item>
    <n-form-item path="password" label="Password">
      <n-input
        v-model:value="formModel.password"
        type="password"
        placeholder="..."
        @input="handlePasswordInput"
        @keydown.enter.prevent
      />
    </n-form-item>
    <n-form-item ref="rPasswordFormItemRef" first path="passwordRepeat" label="Repeat Password">
      <n-input
        v-model:value="formModel.passwordRepeat"
        :disabled="!formModel.password"
        type="password"
        placeholder="..."
        @keydown.enter.prevent
      />
    </n-form-item>
    <n-form-item path="firstName" label="First Name">
      <n-input
        v-model:value="formModel.firstName"
        type="text"
        placeholder="..."
        @keydown.enter.prevent
      />
    </n-form-item>
    <n-form-item path="lastName" label="Last Name">
      <n-input
        v-model:value="formModel.lastName"
        type="text"
        placeholder="..."
        @keydown.enter.prevent
      />
    </n-form-item>
    <n-row :gutter="[0, 24]">
      <n-col :span="24">
        <div style="display: flex; justify-content: flex-end">
          <n-button type="primary" @click="handleRegisterButtonClick"> Register </n-button>
        </div>
      </n-col>
    </n-row>
  </n-form>
</template>
