<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAuthStore, LoginTemplatePromise } from '@/stores';
import {
  type FormInst,
  type FormRules,
  NForm,
  NFormItem,
  NInput,
  NButton,
  NSpace,
  NModal,
} from 'naive-ui';
import { ref, onMounted, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';
import { useMessages } from '@/messages';
import type { RouteLocationRaw } from 'vue-router';

const auth = useAuthStore();
const { message } = useMessages();
const router = useRouter();
const { t } = useI18n({ useScope: 'global' });

const initialFormModel = () => ({
  email: null,
  password: null,
});

const formModel = ref<Record<string, string | null>>(initialFormModel());
const formRef = ref<FormInst | null>(null);
const firstInputRef = ref<HTMLInputElement | null>(null);

const formRules: FormRules = {
  email: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.user.email') }),
      // trigger: 'blur',
    },
  ],
  password: [
    {
      required: true,
      message: () => t('forms.rulesFeedback.isRequired', { x: t('models.user.password') }),
      trigger: 'blur',
    },
  ],
};

function resetForm() {
  formModel.value = initialFormModel();
  formRef.value?.restoreValidation();
}

function switchToRegistration() {
  resetForm();
  router.push({ name: 'register' });
}

async function handleLoginClick(
  resolveLogin: (res: boolean | Promise<boolean>) => void,
  nextRoute: RouteLocationRaw | null | undefined
) {
  formRef.value
    ?.validate(async (errors) => {
      if (errors) return;
      resolveLogin(
        auth.login(formModel.value.email || '', formModel.value.password || '', nextRoute)
      );
      resetForm();
    })
    .catch(() => {
      message.error(t('errors.followFormRules'));
    });
}

function handleForgotPasswordClick() {
  message.info('So you forgot your password? This is not implemented, yet!');
}

onMounted(() => {
  nextTick(() => {
    firstInputRef.value?.focus();
  });
});
</script>

<template>
  <LoginTemplatePromise v-slot="{ args, resolve, reject, isResolving }">
    <n-modal
      show
      preset="card"
      size="large"
      class="tekst-modal"
      @close="reject(null)"
      @mask-click="reject(null)"
      to="#app-container"
      closable
      embedded
    >
      <div class="form-container" style="margin-bottom: 1rem">
        <h2 style="text-align: center">{{ $t('account.login.heading') }}</h2>
        <div v-show="args[0]" class="login-message">{{ args[0] }}</div>
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
          <n-form-item path="password" :label="$t('models.user.password')">
            <n-input
              v-model:value="formModel.password"
              type="password"
              :placeholder="$t('models.user.password')"
              @keyup.enter="handleLoginClick(resolve, args[1])"
            />
          </n-form-item>
        </n-form>

        <div style="display: flex; justify-content: flex-end">
          <n-button
            text
            :focusable="false"
            style="margin-bottom: 2rem; font-size: var(--app-ui-font-size-mini)"
            @click="handleForgotPasswordClick"
          >
            {{ $t('account.forgotPassword') }}
          </n-button>
        </div>

        <n-space vertical :size="12">
          <n-button
            block
            type="primary"
            @click="handleLoginClick(resolve, args[1])"
            :loading="isResolving"
            :disabled="isResolving"
          >
            {{ $t('account.loginBtn') }}
          </n-button>
          <n-button v-if="args[2]" secondary block @click="reject(switchToRegistration())">
            {{ $t('account.switchToRegister') }}
          </n-button>
        </n-space>
      </div>
    </n-modal>
  </LoginTemplatePromise>
</template>

<style scoped>
.login-message {
  padding-bottom: 1rem;
}
</style>
