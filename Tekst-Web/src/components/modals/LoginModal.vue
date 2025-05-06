<script setup lang="ts">
import { POST } from '@/api';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import { useMessages } from '@/composables/messages';
import { accountFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { LoginIcon } from '@/icons';
import { useAuthStore } from '@/stores';
import { NButton, NFlex, NForm, NFormItem, NInput, type FormInst, type InputInst } from 'naive-ui';
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import LabeledSwitch from '@/components/LabeledSwitch.vue';

interface LoginCredentialsModel {
  email: string | null;
  password: string | null;
  persistent?: boolean;
}

const auth = useAuthStore();
const { message } = useMessages();
const router = useRouter();

const initialFormModel: () => LoginCredentialsModel = () => ({
  email: import.meta.env.DEV ? 'admin@tekst.dev' : null,
  password: import.meta.env.DEV ? 'poiPOI098' : null,
  persistent: false,
});

const formModel = ref<LoginCredentialsModel>(initialFormModel());
const formRef = ref<FormInst | null>(null);
const emailInputRef = ref<InputInst | null>(null);

function resetForm() {
  formModel.value = initialFormModel();
  formRef.value?.restoreValidation();
}

function switchToRegistration() {
  resetForm();
  auth.closeLoginModal(false);
  router.push({ name: 'register' });
}

function handleLoginClick() {
  formRef.value
    ?.validate((errors) => {
      if (errors) return;
      auth.login(
        formModel.value.email || '',
        formModel.value.password || '',
        formModel.value.persistent || false
      );
      resetForm();
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    });
}

async function handleForgotPasswordClick() {
  if (formModel.value.email && /^.+@.+\.\w+$/.test(formModel.value.email)) {
    const { error } = await POST('/auth/forgot-password', {
      body: { email: formModel.value.email },
    });
    if (!error) {
      message.info(
        $t('account.forgotPassword.sentResetLink', { email: formModel.value.email }),
        undefined,
        10
      );
    }
    resetForm();
    auth.closeLoginModal(false);
  } else {
    message.error($t('account.forgotPassword.invalidEmail'));
  }
}
</script>

<template>
  <generic-modal
    v-model:show="auth.loginModalState.show"
    width="narrow"
    :title="$t('common.login')"
    :icon="LoginIcon"
    @close="auth.closeLoginModal(false)"
    @mask-click="auth.closeLoginModal(false)"
    @after-enter="emailInputRef?.focus()"
  >
    <div v-show="auth.loginModalState.message" class="login-message mb-lg">
      {{ auth.loginModalState.message }}
    </div>
    <n-form
      ref="formRef"
      :model="formModel"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <!-- username/email -->
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
          :disabled="auth.loginModalState.loading"
          @keydown.enter.prevent
        />
      </n-form-item>
      <!-- password -->
      <n-form-item
        path="password"
        :rule="accountFormRules.loginPassword"
        :label="$t('models.user.password')"
      >
        <n-input
          v-model:value="formModel.password"
          type="password"
          show-password-on="mousedown"
          :placeholder="$t('models.user.password')"
          :disabled="auth.loginModalState.loading"
          @keyup.enter="handleLoginClick"
        />
      </n-form-item>
      <!-- persistent login -->
      <n-form-item :show-label="false">
        <labeled-switch
          v-model="formModel.persistent"
          :label="$t('account.rememberMe')"
          size="small"
        />
      </n-form-item>
    </n-form>

    <n-flex justify="end">
      <n-button
        text
        :focusable="false"
        :disabled="auth.loginModalState.loading"
        class="text-tiny mb-lg"
        @click="handleForgotPasswordClick"
      >
        {{ $t('account.forgotPassword.forgotPassword') }}
      </n-button>
    </n-flex>

    <button-shelf>
      <template #start>
        <n-button
          v-if="auth.loginModalState.showRegisterLink"
          secondary
          type="primary"
          @click="switchToRegistration"
        >
          {{ $t('account.switchToRegister') }}
        </n-button>
      </template>
      <n-button
        type="primary"
        :loading="auth.loginModalState.loading"
        :disabled="auth.loginModalState.loading"
        @click="handleLoginClick"
      >
        {{ $t('common.login') }}
      </n-button>
    </button-shelf>
  </generic-modal>
</template>

<style scoped>
.login-message {
  text-align: center;
}
</style>
