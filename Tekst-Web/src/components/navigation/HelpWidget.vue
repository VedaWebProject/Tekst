<script setup lang="ts">
import GuidedTour from '@/components/GuidedTour.vue';
import { $t } from '@/i18n';
import { HelpOverviewIcon, QuestionMarkIcon, TourIcon } from '@/icons';
import { delay, renderIcon } from '@/utils';
import { NButton, NDropdown, NIcon } from 'naive-ui';
import { inject, type Ref } from 'vue';
import { useRouter } from 'vue-router';

const emit = defineEmits(['done']);
const router = useRouter();
const guidedTourRef = inject('guidedTourRef') as Ref<typeof GuidedTour>;

const options = [
  {
    label: () => $t('tour.heading'),
    key: 'tour',
    icon: renderIcon(TourIcon),
  },
  {
    label: () => $t('help.heading'),
    key: 'help',
    icon: renderIcon(HelpOverviewIcon),
  },
];

async function handleSelect(key: string) {
  emit('done');
  if (key === 'tour') {
    await delay(200);
    guidedTourRef.value.start();
  } else if (key === 'help') {
    router.push({ name: 'help' });
  }
}
</script>

<template>
  <n-dropdown trigger="hover" :options="options" @select="handleSelect">
    <n-button secondary circle size="large" :focusable="false">
      <template #icon>
        <n-icon :component="QuestionMarkIcon" />
      </template>
    </n-button>
  </n-dropdown>
</template>
