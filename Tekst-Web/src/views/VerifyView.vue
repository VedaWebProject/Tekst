<script setup lang="ts">
import { POST } from '@/api';
import { useErrors } from '@/composables/errors';
import { $t } from '@/i18n';
import { CheckCircleIcon, HourglassIcon, KeyOffIcon } from '@/icons';
import { NEmpty, NIcon } from 'naive-ui';
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

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
  <n-empty v-if="!verified && !error" :description="$t('common.loading')">
    <template #icon>
      <n-icon :component="HourglassIcon" />
    </template>
  </n-empty>
  <n-empty v-else-if="error" :description="error">
    <template #icon>
      <n-icon :component="KeyOffIcon" />
    </template>
  </n-empty>
  <n-empty v-else :description="$t('account.verify.success')">
    <template #icon>
      <n-icon :component="CheckCircleIcon" />
    </template>
  </n-empty>
</template>
