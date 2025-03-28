<script setup lang="ts">
import { POST } from '@/api';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import { useMessages } from '@/composables/messages';
import { accountFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import type { FormInst, FormItemInst, FormItemRule } from 'naive-ui';
import { NButton, NForm, NFormItem, NInput } from 'naive-ui';
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

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
    ?.validate(async (validationErrors) => {
      if (validationErrors) return;
      const { error } = await POST('/auth/reset-password', {
        body: {
          password: passwordFormModel.value.password || '',
          token: token || '',
        },
      });
      if (!error) {
        message.success($t('account.resetPassword.success'), undefined, 10);
      }
      router.push({ name: 'home' });
      loading.value = false;
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
      loading.value = false;
    });
}

onMounted(() => {
  if (!token) router.push({ name: 'home' });
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
        :disabled="loading"
        label-placement="top"
        label-width="auto"
        require-mark-placement="right-hanging"
      >
        <n-form-item path="password" :label="$t('models.user.password')">
          <n-input
            ref="firstInputRef"
            v-model:value="passwordFormModel.password"
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
            v-model:value="passwordFormModel.passwordRepeat"
            type="password"
            show-password-on="mousedown"
            :disabled="!passwordFormModel.password || loading"
            :placeholder="$t('register.repeatPassword')"
            @keyup.enter="handlePasswordSave"
          />
        </n-form-item>
      </n-form>
      <button-shelf top-gap>
        <n-button type="primary" :loading="loading" :disabled="loading" @click="handlePasswordSave">
          {{ $t('common.save') }}
        </n-button>
      </button-shelf>
    </div>
  </div>
</template>
