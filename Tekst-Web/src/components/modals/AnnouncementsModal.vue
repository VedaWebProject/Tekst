<script setup lang="ts">
import GenericModal from '@/components/generic/GenericModal.vue';
import HydratedHtml from '@/components/generic/HydratedHtml.vue';
import { $t } from '@/i18n';
import { AnnouncementsIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { hashCode, pickTranslation } from '@/utils';
import { useStorage } from '@vueuse/core';
import { NFlex, NSelect } from 'naive-ui';
import { computed, onMounted, ref } from 'vue';

defineProps<{ loading?: boolean }>();

const state = useStateStore();
const choiceStored = useStorage('announcements', 'ifChanged', localStorage);

const choice = ref<'always' | 'ifChanged' | 'never'>('always');
const options = computed(() => [
  {
    label: $t('common.always'),
    value: 'always',
  },
  {
    label: $t('announcements.ifChanged'),
    value: 'ifChanged',
  },
  {
    label: $t('common.never'),
    value: 'never',
  },
]);

const announcementsHtml = computed(() =>
  pickTranslation(state.pf?.state.announcements, state.locale)
);

function saveChoice() {
  if (choice.value === 'never') {
    choiceStored.value = 'never';
  } else if (choice.value === 'always') {
    choiceStored.value = 'always';
  } else if (choice.value === 'ifChanged') {
    choiceStored.value = hashCode(JSON.stringify(state.pf?.state.announcements)).toString();
  }
}

onMounted(() => {
  // load announcement auto-display choice
  choice.value =
    choiceStored.value !== 'always' && choiceStored.value !== 'never'
      ? 'ifChanged'
      : choiceStored.value;
  // show announcements modal?
  if (
    !!state.pf?.state.announcements?.length &&
    (choice.value === 'always' ||
    (choice.value === 'ifChanged' &&
      choiceStored.value !== hashCode(JSON.stringify(state.pf?.state.announcements)).toString()))
  ) {
    state.showAnnouncementsModal = true;
  }
});
</script>

<template>
  <generic-modal
    :show="state.showAnnouncementsModal"
    :title="state.pf?.state.platformName || $t('announcements.announcement', 2)"
    :icon="AnnouncementsIcon"
    width="wide"
    @update:show="(v) => (state.showAnnouncementsModal = v)"
    @after-leave="saveChoice"
  >
    <hydrated-html :html="announcementsHtml" />
    <n-flex justify="flex-end" align="center" class="mt-lg" :title="$t('common.localStorageHint')">
      <div style="text-wrap: nowrap">{{ $t('announcements.autoShowPrefix') }}</div>
      <n-select
        v-model:value="choice"
        :options="options"
        :consistent-menu-width="false"
        style="width: auto"
      />
    </n-flex>
  </generic-modal>
</template>
