<script setup lang="ts">
import { useGuidedTour } from '@/composables/tour';
import { $t } from '@/i18n';
import { HelpOverviewIcon, QuestionMarkIcon, TourIcon } from '@/icons';
import { renderIcon } from '@/utils';
import { NButton, NDropdown, NIcon } from 'naive-ui';
import { useRouter } from 'vue-router';

const emit = defineEmits(['done']);
const router = useRouter();
const { start: startGuidedTour } = useGuidedTour();

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
    startGuidedTour();
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

<style>
.driver-popover {
  background-color: var(--base-color);
  border-radius: var(--border-radius);
  max-width: 380px;
  box-shadow: var(--affix-box-shadow);
  font-family: var(--font-family-ui);
}

.driver-popover .driver-popover-arrow-side-left.driver-popover-arrow {
  border-left-color: var(--base-color);
}

.driver-popover .driver-popover-arrow-side-right.driver-popover-arrow {
  border-right-color: var(--base-color);
}

.driver-popover .driver-popover-arrow-side-top.driver-popover-arrow {
  border-top-color: var(--base-color);
}

.driver-popover .driver-popover-arrow-side-bottom.driver-popover-arrow {
  border-bottom-color: var(--base-color);
}

.driver-popover .driver-popover-title {
  color: var(--text-color);
  font-size: var(--font-size);
  font-weight: bold;
  font-family: var(--font-family-ui);
}

.driver-popover .driver-popover-description {
  color: var(--text-color);
  font-size: var(--font-size-small);
  font-weight: normal;
  font-family: var(--font-family-ui);
}

.driver-popover footer.driver-popover-footer {
  margin-top: var(--gap-md);
  padding-top: var(--gap-md);
  border-top: 1px solid var(--main-bg-color);
  font-family: var(--font-family-ui);
}

.driver-popover .driver-popover-navigation-btns > button {
  background-color: var(--primary-color);
  color: var(--base-color);
  text-shadow: none;
  border: none;
  border-radius: var(--border-radius);
  padding: 8px 12px 6px 12px;
  font-size: var(--font-size-small);
  transition: filter 0.2s ease-in-out;
  font-family: var(--font-family-ui);
}

.driver-popover .driver-popover-progress-text {
  opacity: 0.9;
  font-size: var(--font-size-small);
  font-family: var(--font-family-ui);
}

.driver-popover .driver-popover-navigation-btns > button:hover {
  filter: brightness(1.15);
}
</style>
