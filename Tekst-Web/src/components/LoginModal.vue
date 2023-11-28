<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores';
import { type FormInst, NForm, NFormItem, NInput, NButton, NModal } from 'naive-ui';
import { ref, onMounted, nextTick } from 'vue';
import { $t } from '@/i18n';
import { useMessages } from '@/messages';
import type { RouteLocationRaw } from 'vue-router';
import { accountFormRules } from '@/formRules';
import { POST } from '@/api';
import ButtonFooter from '@/components/ButtonFooter.vue';
import { LoginTemplatePromise } from '@/templatePromises';

const auth = useAuthStore();
const { message } = useMessages();
const router = useRouter();

const initialFormModel = () => ({
  email: null,
  password: null,
});

const formModel = ref<Record<string, string | null>>(initialFormModel());
const formRef = ref<FormInst | null>(null);
const emailInputRef = ref<HTMLInputElement | null>(null);

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
      message.error($t('errors.followFormRules'));
    });
}

async function handleForgotPasswordClick(resolveLogin: (res: boolean | Promise<boolean>) => void) {
  if (formModel.value.email && /^.+@.+\.\w+$/.test(formModel.value.email)) {
    const { error } = await POST('/auth/forgot-password', {
      body: { email: formModel.value.email },
    });
    if (error) {
      message.error($t('errors.unexpected'), error, 10);
    } else {
      message.info(
        $t('account.forgotPassword.sentResetLink', { email: formModel.value.email }),
        undefined,
        10
      );
    }
    resetForm();
    resolveLogin(false);
  } else {
    message.error($t('account.forgotPassword.invalidEmail'));
  }
}

onMounted(() => {
  nextTick(() => {
    emailInputRef.value?.focus();
  });
});
</script>

<template>
  <LoginTemplatePromise v-slot="{ args, resolve, reject, isResolving }">
    <n-modal
      show
      preset="card"
      size="large"
      class="tekst-modal tekst-modal-narrow"
      to="#app-container"
      :closable="false"
      embedded
      @close="reject(null)"
      @mask-click="reject(null)"
    >
      <div class="form-container">
        <h2 style="text-align: center">{{ $t('account.login.heading') }}</h2>
        <div v-show="args[0]" class="login-message">{{ args[0] }}</div>
        <n-form
          ref="formRef"
          :model="formModel"
          label-placement="top"
          label-width="auto"
          require-mark-placement="right-hanging"
        >
          <n-form-item
            path="email"
            :rule="accountFormRules.loginEmail"
            :label="$t('models.user.email')"
          >
            <n-input
              ref="emailInputRef"
              v-model:value="formModel.email"
              type="text"
              :placeholder="$t('models.user.email')"
              :disabled="isResolving"
              @keydown.enter.prevent
            />
          </n-form-item>
          <n-form-item
            path="password"
            :rule="accountFormRules.loginPassword"
            :label="$t('models.user.password')"
          >
            <n-input
              v-model:value="formModel.password"
              type="password"
              :placeholder="$t('models.user.password')"
              :disabled="isResolving"
              @keyup.enter="handleLoginClick(resolve, args[1])"
            />
          </n-form-item>
        </n-form>

        <div style="display: flex; justify-content: flex-end">
          <n-button
            text
            :focusable="false"
            style="margin-bottom: 1rem; font-size: var(--app-ui-font-size-mini)"
            @click="handleForgotPasswordClick(resolve)"
          >
            {{ $t('account.forgotPassword.forgotPassword') }}
          </n-button>
        </div>
      </div>
      <ButtonFooter>
        <n-button v-if="args[2]" secondary @click="reject(switchToRegistration())">
          {{ $t('account.switchToRegister') }}
        </n-button>
        <n-button
          type="primary"
          :loading="isResolving"
          :disabled="isResolving"
          @click="handleLoginClick(resolve, args[1])"
        >
          {{ $t('account.loginBtn') }}
        </n-button>
      </ButtonFooter>
    </n-modal>
  </LoginTemplatePromise>
</template>

<style scoped>
.login-message {
  margin-bottom: 1.5rem;
  text-align: center;
}
</style>
