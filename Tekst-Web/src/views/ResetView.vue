<script setup lang="ts">
import { POST } from '@/api';
import { accountFormRules } from '@/formRules';
import { useMessages } from '@/messages';
import type { FormInst, FormItemInst, FormItemRule } from 'naive-ui';
import { ref } from 'vue';
import { $t } from '@/i18n';
import { NInput, NForm, NFormItem, NButton } from 'naive-ui';
import { useRoute } from 'vue-router';
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import ButtonFooter from '@/components/ButtonFooter.vue';

const { message } = useMessages();
const route = useRoute();
const router = useRouter();
const token = route.query.token?.toString();

const initialPasswordFormModel = () => ({
  password: '',
  passwordRepeat: '',
});

const passwordFormRef = ref<FormInst | null>(null);
const passwordFormModel = ref<Record<string, string | null>>(initialPasswordFormModel());

const rPasswordFormItemRef = ref<FormItemInst | null>(null);
const firstInputRef = ref<HTMLInputElement | null>(null);
const loading = ref(false);

const passwordRepeatMatchRule = {
  validator: (_: FormItemRule, value: string) =>
    !!value && !!passwordFormModel.value.password && value === passwordFormModel.value.password,
  message: () => $t('models.user.formRulesFeedback.passwordRepNoMatch'),
  trigger: ['input', 'blur', 'password-input'],
};

function handlePasswordInput() {
  if (passwordFormModel.value.reenteredPassword) {
    rPasswordFormItemRef.value?.validate({ trigger: 'password-input' });
  }
}

async function handlePasswordSave() {
  loading.value = true;
  passwordFormRef.value
    ?.validate(async (errors) => {
      !errors &&
        (async () => {
          const { error } = await POST('/auth/reset-password', {
            body: {
              password: passwordFormModel.value.password || '',
              token: token || '',
            },
          });
          if (!error) {
            message.success($t('account.resetPassword.success'), undefined, 10);
            router.push({ name: 'home' });
          } else {
            if (error.detail === 'RESET_PASSWORD_BAD_TOKEN') {
              message.error($t('account.resetPassword.badToken'));
            } else {
              message.error($t('errors.unexpected'), error);
            }
            router.push({ name: 'home' });
          }
          loading.value = false;
        })();
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
      loading.value = false;
    });
}

onMounted(() => {
  !token && router.push({ name: 'home' });
});
</script>

<template>
  <h1 style="text-align: center">{{ $t('account.resetPassword.heading') }}</h1>
  <div class="form-container">
    <div class="content-block">
      <n-form
        ref="passwordFormRef"
        :model="passwordFormModel"
        :rules="accountFormRules"
        label-placement="top"
        label-width="auto"
        require-mark-placement="right-hanging"
      >
        <n-form-item path="password" :label="$t('models.user.password')">
          <n-input
            ref="firstInputRef"
            v-model:value="passwordFormModel.password"
            type="password"
            :placeholder="$t('models.user.password')"
            :disabled="loading"
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
            v-model:value="passwordFormModel.passwordRepeat"
            type="password"
            :disabled="!passwordFormModel.password || loading"
            :placeholder="$t('register.repeatPassword')"
            @keyup.enter="handlePasswordSave"
          />
        </n-form-item>
      </n-form>
      <ButtonFooter>
        <n-button type="primary" :loading="loading" :disabled="loading" @click="handlePasswordSave">
          {{ $t('general.saveAction') }}
        </n-button>
      </ButtonFooter>
    </div>
  </div>
</template>
