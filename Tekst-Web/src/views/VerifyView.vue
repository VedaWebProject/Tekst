<script setup lang="ts">
import { POST } from '@/api';
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { $t } from '@/i18n';
import { useRouter } from 'vue-router';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import { KeyOffIcon, CheckCircleIcon } from '@/icons';
import { useErrors } from '@/composables/errors';

const route = useRoute();
const router = useRouter();
const errors = useErrors();
const token = route.query.token?.toString();
const verified = ref(false);
const error = ref<string | null>(null);

onMounted(async () => {
  if (token) {
    const { error: apiError } = await POST('/auth/verify', { body: { token } });
    if (!apiError) {
      verified.value = true;
    } else {
      error.value = errors.msg(apiError, false);
    }
  } else {
    router.push({ name: 'home' });
  }
});
</script>

<template>
  <huge-labelled-icon
    :message="error ? error : $t('account.verify.success')"
    :loading="!error && !verified"
    :icon="error ? KeyOffIcon : CheckCircleIcon"
  />
</template>
