<script setup lang="ts">
import { useApi } from '@/api';
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import type { ErrorModel } from '@/api';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import HugeLabeledIcon from '@/components/HugeLabeledIcon.vue';

import CheckCircleTwotone from '@vicons/material/CheckCircleTwotone';
import KeyOffTwotone from '@vicons/material/KeyOffTwotone';

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
  <huge-labeled-icon
    :message="error ? error : $t('account.verify.success')"
    :loading="!error && !verified"
    :icon="error ? KeyOffTwotone : CheckCircleTwotone"
  />
</template>
