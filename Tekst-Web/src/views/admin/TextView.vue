<script setup lang="ts">
import { DELETE } from '@/api';
import { dialogProps } from '@/common';
import IconHeading from '@/components/generic/IconHeading.vue';
import { useMessages } from '@/composables/messages';
import { usePlatformData } from '@/composables/platformData';
import TextLevelsForm from '@/forms/texts/TextLevelsForm.vue';
import TextLocationsForm from '@/forms/texts/TextLocationsForm.vue';
import TextSettingsForm from '@/forms/texts/TextSettingsForm.vue';
import { $t } from '@/i18n';
import { AddIcon, DeleteIcon, TextsIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { NButton, NFlex, NIcon, NTabPane, NTabs, useDialog, type TabsInst } from 'naive-ui';
import { computed, ref, watch } from 'vue';
import { useRouter } from 'vue-router';

defineProps<{
  textSlug?: string;
}>();

const state = useStateStore();
const router = useRouter();
const dialog = useDialog();
const { message } = useMessages();
const { loadPlatformData } = usePlatformData();

const loading = ref(false);

const tabsRef = ref<TabsInst>();

const textCanBeDeleted = computed(() => {
  if (!state.pf) return false;
  if (state.text?.isActive) {
    return state.pf.texts.filter((t) => t.isActive).length > 1;
  } else {
    return state.pf.texts.length > 1;
  }
});

async function handleDelete() {
  dialog.warning({
    title: $t('common.warning'),
    content: $t('texts.settings.warnDeleteText', { title: state.text?.title || '?' }),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      loading.value = true;
      const { error } = await DELETE('/texts/{id}', {
        params: { path: { id: state.text?.id || '' } },
      });
      if (!error) {
        message.success($t('texts.settings.msgDeleted', { title: state.text?.title || '?' }));
        await loadPlatformData();
        state.text = state.defaultText;
        router.replace({ name: 'home' });
      }
      loading.value = false;
    },
  });
}

watch(
  () => state.locale,
  () => {
    setTimeout(() => {
      tabsRef.value?.syncBarPosition();
    }, 100);
  }
);
</script>

<template>
  <n-flex align="center">
    <icon-heading level="1" :icon="TextsIcon" style="margin-bottom: 0">
      {{ state.text?.title || $t('common.text') }}
    </icon-heading>
    <n-flex :wrap="false" justify="flex-end" style="flex: 2">
      <n-button secondary type="error" :disabled="!textCanBeDeleted" @click="handleDelete">
        <template #icon>
          <n-icon :component="DeleteIcon" />
        </template>
        {{ $t('common.delete') }}
      </n-button>
      <n-button type="primary" @click="router.push({ name: 'newText' })">
        <template #icon>
          <n-icon :component="AddIcon" />
        </template>
        {{ $t('admin.newText.heading') }}
      </n-button>
    </n-flex>
  </n-flex>

  <div class="content-block">
    <n-tabs
      ref="tabsRef"
      type="line"
      :placement="state.smallScreen ? 'top' : 'left'"
      :pane-class="state.smallScreen ? 'mt-md' : 'ml-lg'"
    >
      <!-- SETTINGS -->
      <n-tab-pane :tab="$t('common.settings')" name="settings">
        <text-settings-form />
      </n-tab-pane>

      <!-- LEVELS -->
      <n-tab-pane :tab="$t('common.level', 2)" name="levels">
        <text-levels-form />
      </n-tab-pane>

      <!-- LOCATIONS -->
      <n-tab-pane :tab="$t('common.location', 2)" name="locations">
        <text-locations-form />
      </n-tab-pane>
    </n-tabs>
  </div>
</template>
