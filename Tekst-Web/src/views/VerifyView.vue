<script setup lang="ts">
import { POST } from '@/api';
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { $t } from '@/i18n';
import { useRouter } from 'vue-router';
import HugeLabeledIcon from '@/components/generic/HugeLabeledIcon.vue';

import { KeyOffIcon, CheckCircleIcon } from '@/icons';

const route = useRoute();
const router = useRouter();
const token = route.query.token?.toString();
const verified = ref(false);
const error = ref<string | null>(null);

onMounted(async () => {
  if (token) {
    const { error: apiError } = await POST('/auth/verify', { body: { token } });
    if (!apiError) {
      verified.value = true;
    } else {
      if (apiError.detail === 'VERIFY_USER_BAD_TOKEN') {
        error.value = $t('account.verify.badToken');
      } else if (apiError.detail === 'VERIFY_USER_ALREADY_VERIFIED') {
        error.value = $t('account.verify.alreadyVerified');
      } else {
        error.value = $t('errors.unexpected');
      }
    }
  } else {
    router.push({ name: 'home' });
  }
});
</script>

<template>
  <HugeLabeledIcon
    :message="error ? error : $t('account.verify.success')"
    :loading="!error && !verified"
    :icon="error ? KeyOffIcon : CheckCircleIcon"
  />
</template>
