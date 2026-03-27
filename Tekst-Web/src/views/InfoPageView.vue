<script setup lang="ts">
import type { ClientSegmentRead } from '@/api';
import HydratedHtml from '@/components/generic/HydratedHtml.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { usePlatformData } from '@/composables/platformData';
import { EditIcon } from '@/icons';
import { useAuthStore, useStateStore } from '@/stores';
import { NButton, NIcon, NSpin } from 'naive-ui';
import { ref, watchEffect, type Component } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps<{
  pageKey?: string;
  icon?: Component;
}>();

const state = useStateStore();
const auth = useAuthStore();
const loading = ref(false);
const { getSegment } = usePlatformData();
const router = useRouter();

const page = ref<ClientSegmentRead>();

function handleEditClick() {
  if (!page.value) return;
  // the only system segment that is rendered with
  // the InfoPageView component is the home page
  const name = page.value.key.startsWith('system') ? 'adminSegments' : 'adminInfoPages';
  router.push({ name, hash: `#page=${page.value.id}` });
}

watchEffect(async () => {
  loading.value = true;
  page.value = await getSegment(props.pageKey, state.locale);
  if (!page.value) {
    router.replace({ name: 'browse' });
  }
  loading.value = false;
});
</script>

<template>
  <n-spin v-if="loading" :description="$t('common.loading')" class="centered-spin" />
  <template v-else-if="page">
    <icon-heading v-if="page.title" level="1" :icon="icon">
      {{ page.title }}
      <n-button
        v-if="!!auth.user?.isSuperuser"
        circle
        quaternary
        size="small"
        :title="$t('admin.infoPages.editPage')"
        @click="handleEditClick"
      >
        <template #icon>
          <n-icon :component="EditIcon" />
        </template>
      </n-button>
    </icon-heading>
    <div class="content-block" style="padding: 1.2rem">
      <hydrated-html :html="page.html" />
    </div>
  </template>
</template>
