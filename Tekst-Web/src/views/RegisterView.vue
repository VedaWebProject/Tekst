<script setup lang="ts">
import type { UserCreate } from '@/api';
import { POST } from '@/api';
import IconHeading from '@/components/generic/IconHeading.vue';
import { useMessages } from '@/composables/messages';
import { usePlatformData } from '@/composables/platformData';
import { accountFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { UserIcon } from '@/icons';
import router from '@/router';
import { useAuthStore } from '@/stores';
import SegmentRenderer from '@/components/SegmentRenderer.vue';
import {
  type FormInst,
  type FormItemInst,
  type FormItemRule,
  NButton,
  NFlex,
  NForm,
  NFormItem,
  NInput,
  NDivider,
} from 'naive-ui';
import { computed, nextTick, onMounted, ref } from 'vue';

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

const introTextPresent = computed(
  () => !!pfData.value?.systemSegments.find((s) => s.key === 'systemRegisterIntro')
);

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
    const activationNeeded = !pfData.value?.security.usersActiveByDefault;
    const activationHint = activationNeeded
      ? $t('register.activationNeededHint')
      : $t('register.activationNotNeededHint');
    message.success(
      `${$t('register.success')} ${activationHint}`,
      undefined,
      activationNeeded ? 20 : 5
    );
    // if no activation is needed, send verification link right away
    if (!activationNeeded && !pfData.value?.security.closedMode) {
      const { error: verifyTokenError } = await POST('/auth/request-verify-token', {
        body: { email: formModel.value.email || '' },
      });
      if (!verifyTokenError) {
        message.warning($t('account.settings.msgVerifyEmailWarning'));
      }
    }
    router.push({ name: 'home' });
  }
  loading.value = false;
}

function handleRegisterClick() {
  loading.value = true;
  formRef.value
    ?.validate((errors) => {
      if (!errors) registerUser();
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
    (!auth.loggedIn && pfData.value?.security.closedMode)
  ) {
    router.push({ name: 'home' });
  }
  nextTick(() => {
    firstInputRef.value?.focus();
  });
});
</script>

<template>
  <div :class="{ 'form-container': !introTextPresent }">
    <icon-heading level="1" :icon="UserIcon">
      {{ $t('register.heading') }}
    </icon-heading>

    <div class="content-block">
      <segment-renderer v-if="introTextPresent" segment-key="systemRegisterIntro" />
      <n-divider v-if="introTextPresent" />

      <div :class="{ 'form-container': introTextPresent }">
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
              show-password-on="mousedown"
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
              show-password-on="mousedown"
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

        <n-flex vertical :size="12" class="mt-lg">
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
  </div>
</template>
