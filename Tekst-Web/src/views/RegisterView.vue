<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import { $t } from '@/i18n';
import {
  type FormInst,
  type FormItemInst,
  type FormItemRule,
  NForm,
  NFormItem,
  NInput,
  NButton,
  NFlex,
} from 'naive-ui';
import type { UserCreate } from '@/api';
import { POST } from '@/api';
import { useMessages } from '@/composables/messages';
import { usePlatformData } from '@/composables/platformData';
import { useAuthStore } from '@/stores';
import { accountFormRules } from '@/forms/formRules';
import router from '@/router';
import { UserIcon } from '@/icons';
import IconHeading from '@/components/generic/IconHeading.vue';

const auth = useAuthStore();
const { message } = useMessages();
const { pfData } = usePlatformData();

const initialFormModel = () => ({
  email: null,
  username: null,
  password: null,
  passwordRepeat: null,
  name: null,
  affiliation: null,
});

const formModel = ref<Record<string, string | null>>(initialFormModel());
const formRef = ref<FormInst | null>(null);
const rPasswordFormItemRef = ref<FormItemInst | null>(null);
const firstInputRef = ref<HTMLInputElement | null>(null);
const loading = ref(false);

const passwordRepeatMatchRule = {
  validator: (rule: FormItemRule, value: string) =>
    !!value && !!formModel.value.password && value === formModel.value.password,
  message: () => $t('models.user.formRulesFeedback.passwordRepNoMatch'),
  trigger: ['input', 'blur', 'password-input'],
};

function handlePasswordInput() {
  if (formModel.value.reenteredPassword) {
    rPasswordFormItemRef.value?.validate({ trigger: 'password-input' });
  }
}

async function registerUser() {
  const { error } = await POST('/auth/register', {
    body: formModel.value as unknown as UserCreate,
  });

  if (!error) {
    const activationNeeded = !pfData.value?.security?.usersActiveByDefault;
    const activationHint = activationNeeded
      ? $t('register.activationNeededHint')
      : $t('register.activationNotNeededHint');
    message.success(
      `${$t('register.success')} ${activationHint}`,
      undefined,
      activationNeeded ? 20 : 5
    );
    // if no activation is needed, send verification link right away
    if (!activationNeeded && !pfData.value?.security?.closedMode) {
      const { error: verifyTokenError } = await POST('/auth/request-verify-token', {
        body: { email: formModel.value.email || '' },
      });
      if (!verifyTokenError) {
        message.warning($t('account.settings.msgVerifyEmailWarning'));
      }
    }
    switchToLogin();
  }
  loading.value = false;
}

function handleRegisterClick() {
  loading.value = true;
  formRef.value
    ?.validate((errors) => {
      !errors && registerUser();
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
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
  if (
    (auth.loggedIn && !auth.user?.isSuperuser) ||
    (pfData.value?.security?.closedMode && !auth.loggedIn)
  ) {
    router.push({ name: 'home' });
  }
  nextTick(() => {
    firstInputRef.value?.focus();
  });
});
</script>

<template>
  <div class="form-container">
    <div class="content-block">
      <icon-heading level="1" :icon="UserIcon">
        {{ $t('register.heading') }}
      </icon-heading>
      <n-form
        ref="formRef"
        :model="formModel"
        :rules="accountFormRules"
        :disabled="loading"
        label-placement="top"
        label-width="auto"
        require-mark-placement="right-hanging"
      >
        <n-form-item path="email" :label="$t('models.user.email')">
          <n-input
            ref="firstInputRef"
            v-model:value="formModel.email"
            type="text"
            :placeholder="$t('models.user.email')"
            @keydown.enter.prevent
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
          :rule="accountFormRules.passwordRepeat.concat([passwordRepeatMatchRule])"
          :label="$t('register.repeatPassword')"
        >
          <n-input
            v-model:value="formModel.passwordRepeat"
            type="password"
            :disabled="!formModel.password || loading"
            :placeholder="$t('register.repeatPassword')"
            @keydown.enter.prevent
          />
        </n-form-item>
        <n-form-item path="name" :label="$t('models.user.name')">
          <n-input
            v-model:value="formModel.name"
            type="text"
            :placeholder="$t('models.user.name')"
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

      <n-flex vertical :size="12" style="margin-top: 1rem">
        <n-button
          block
          type="primary"
          :loading="loading"
          :disabled="loading"
          @click="handleRegisterClick"
        >
          {{ $t('register.register') }}
        </n-button>
        <n-button secondary block @click="switchToLogin">
          {{ $t('register.switchToLogin') }}
        </n-button>
      </n-flex>
    </div>
  </div>
</template>
