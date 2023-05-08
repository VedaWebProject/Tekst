<script setup lang="ts">
import { useFormRules } from '@/formRules';
import type { FormInst, FormItemInst, FormItemRule } from 'naive-ui';
import { NButton, NSpace, NInput, NFormItem, NForm } from 'naive-ui';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n({ useScope: 'global' });

const initialEmailFormModel = () => ({
  email: null,
});

const initialPasswordFormModel = () => ({
  password: null,
  passwordRepeat: null,
});

const initialUserDataFormModel = () => ({
  username: null,
  firstName: null,
  lastName: null,
  affiliation: null,
});

const formRules = useFormRules();

const emailFormModel = ref<Record<string, string | null>>(initialEmailFormModel());
const emailFormRef = ref<FormInst | null>(null);

const passwordFormModel = ref<Record<string, string | null>>(initialPasswordFormModel());
const passwordFormRef = ref<FormInst | null>(null);

const userDataFormModel = ref<Record<string, string | null>>(initialUserDataFormModel());
const userDataFormRef = ref<FormInst | null>(null);

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

function handleEmailSave() {}

function handlePasswordSave() {}

function handleUserDataSave() {}
</script>

<template>
  <h1>{{ $t('account.manage.heading') }}</h1>

  <div class="block-container">
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
          :disabled="loading"
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
          :disabled="loading"
        >
          {{ $t('general.saveAction') }}
        </n-button>
      </n-space>
    </div>

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
          :disabled="loading"
        >
          {{ $t('general.saveAction') }}
        </n-button>
      </n-space>
    </div>
  </div>
</template>

<style scoped>
.block-container {
  display: flex;
  align-items: stretch;
  flex-wrap: wrap;
  gap: var(--layout-gap);
  margin-bottom: var(--layout-gap);
}

.block-container > * {
  width: 380px;
  max-width: 100%;
  margin: 0;
}
</style>
