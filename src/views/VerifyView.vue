<script setup lang="ts">
import { useApi } from '@/api';
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { NSpin } from 'naive-ui';
import type { AxiosError } from 'axios';
import type { ErrorModel } from '@/openapi';
import { useI18n } from 'vue-i18n';

const { authApi } = useApi();
const route = useRoute();
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
  }
});
</script>

<template>
  <div class="content-block" style="padding: 2rem; text-align: center">
    <div v-if="verified" style="color: var(--col-success)">
      {{ $t('account.verify.success') }}
    </div>

    <div v-else-if="!error" style="padding: 2rem; text-align: center">
      <n-spin>
        <template #description>
          {{ $t('init.loading') }}
        </template>
      </n-spin>
    </div>

    <div v-else style="color: var(--col-error)">
      {{ error }}
    </div>
  </div>
</template>
