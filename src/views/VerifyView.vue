<script setup lang="ts">
import { useApi } from '@/api';
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import type { AxiosError } from 'axios';
import type { ErrorModel } from '@/openapi';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import TokenActionResult from '@/components/TokenActionResult.vue';

const { authApi } = useApi();
const route = useRoute();
const router = useRouter();
const token = route.query.token?.toString();
const verified = ref(false);
const error = ref<string | null>(null);
const { t } = useI18n({ useScope: 'global' });

onMounted(() => {
  if (token) {
    authApi
      .verifyVerify({ bodyVerifyVerifyAuthVerifyPost: { token } })
      .then(() => {
        verified.value = true;
      })
      .catch((e: AxiosError) => {
        if (e.response) {
          const data = e.response.data as ErrorModel;
          if (data.detail === 'VERIFY_USER_BAD_TOKEN') {
            error.value = t('account.verify.badToken');
          } else if (data.detail === 'VERIFY_USER_ALREADY_VERIFIED') {
            error.value = t('account.verify.alreadyVerified');
          } else {
            error.value = t('errors.unexpected');
          }
        } else {
          error.value = t('errors.unexpected');
        }
      });
  } else {
    router.push({ name: 'home' });
  }
});
</script>

<template>
  <token-action-result
    :message="error ? error : t('account.verify.success')"
    :success="verified"
    :loading="!error && !verified"
  />
</template>
