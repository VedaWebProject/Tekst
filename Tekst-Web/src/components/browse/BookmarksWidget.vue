<script setup lang="ts">
import { type BookmarkRead } from '@/api';
import { usePlatformData } from '@/composables/platformData';
import { useBrowseStore, useStateStore } from '@/stores';
import { NThing, NIcon, NButton, NList, NListItem } from 'naive-ui';
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import PromptModal from '@/components/generic/PromptModal.vue';
import { $t } from '@/i18n';
import { useMessages } from '@/composables/messages';
import GenericModal from '../generic/GenericModal.vue';
import LocationLabel from '@/components/LocationLabel.vue';
import { useBookmarks } from '@/composables/bookmarks';
import { bookmarkFormRules } from '@/forms/formRules';
import { AddIcon, BookIcon, BookmarkFilledIcon, DeleteIcon } from '@/icons';

defineProps<{
  size?: 'small' | 'medium' | 'large';
  color?: string;
  bgColor?: string;
}>();

const browse = useBrowseStore();
const state = useStateStore();
const { pfData } = usePlatformData();
const { message } = useMessages();
const { bookmarks, createBookmark, deleteBookmark } = useBookmarks();
const router = useRouter();

const showModal = ref(false);
const promptModalRef = ref();
const loading = ref(false);
const currentBookmarks = computed(
  () => bookmarks.value.filter((b) => b.textId === state.text?.id) || []
);
const maxCountReached = computed(() => bookmarks.value.length >= 1000);

async function handleDeleteBookmark(e: MouseEvent, bookmarkId: string) {
  e.preventDefault();
  e.stopPropagation();
  loading.value = true;
  await deleteBookmark(bookmarkId);
  loading.value = false;
}

function handleCreateBookmarkClick() {
  if (currentBookmarks.value.find((b) => b.locationId === browse.locationPathHead?.id)) {
    message.error($t('browse.bookmarks.errorBookmarkExists'));
    return;
  }
  promptModalRef.value.open();
}

async function handleCreateModalSubmit(comment: string) {
  loading.value = true;
  await createBookmark(browse.locationPathHead?.id || '', comment);
  loading.value = false;
}

async function handleBookmarkSelect(bookmark: BookmarkRead) {
  showModal.value = false;
  router.replace({
    name: 'browse',
    params: { text: pfData.value?.texts.find((t) => t.id === bookmark.textId)?.slug || '' },
    query: { lvl: bookmark.level, pos: bookmark.position },
  });
}
</script>

<template>
  <n-button
    :size="size"
    :color="bgColor"
    :style="{ color: color }"
    :focusable="false"
    :title="$t('browse.bookmarks.bookmarks')"
    @click="showModal = true"
  >
    <template #icon>
      <n-icon :component="BookmarkFilledIcon" />
    </template>
  </n-button>

  <generic-modal
    v-model:show="showModal"
    :auto-focus="false"
    width="wide"
    :title="$t('browse.bookmarks.bookmarks')"
    :icon="BookmarkFilledIcon"
  >
    <n-list hoverable clickable style="background-color: transparent">
      <n-list-item
        :class="{ disabled: loading || maxCountReached }"
        @click="!loading && handleCreateBookmarkClick()"
      >
        <n-thing content-indented>
          <template #avatar>
            <n-icon :component="AddIcon" size="large" />
          </template>
          <template #header>
            <span v-if="!maxCountReached">
              {{ $t('browse.bookmarks.lblCreate') }}
            </span>
            <span v-else> ({{ $t('browse.bookmarks.maxCountReached') }}) </span>
          </template>
        </n-thing>
      </n-list-item>
      <n-list-item
        v-for="bookmark in currentBookmarks"
        :key="bookmark.id"
        @click="handleBookmarkSelect(bookmark)"
      >
        <n-thing content-indented description-style="font-size: var(--font-size-tiny)">
          <template #avatar>
            <n-icon :component="BookIcon" size="large" />
          </template>
          <template #header>
            <location-label :location-labels="bookmark.locationLabels" />
          </template>
          <template #header-extra>
            <div style="height: 100%; display: flex; align-items: center">
              <n-button
                secondary
                size="small"
                :focusable="false"
                :disabled="loading"
                :loading="loading"
                :title="$t('general.deleteAction')"
                @click="(e) => handleDeleteBookmark(e, bookmark.id)"
              >
                <template #icon>
                  <n-icon :component="DeleteIcon" />
                </template>
              </n-button>
            </div>
          </template>
          <template v-if="bookmark.comment" #description>
            <div style="white-space: pre-wrap">
              {{ bookmark.comment }}
            </div>
          </template>
        </n-thing>
      </n-list-item>
    </n-list>
  </generic-modal>

  <prompt-modal
    ref="promptModalRef"
    multiline
    action-key="createBookmark"
    :title="$t('browse.bookmarks.commentModalTitle')"
    :input-label="$t('browse.bookmarks.commentModalInputLabel')"
    :rows="3"
    :validation-rules="bookmarkFormRules.comment"
    @submit="(_, v) => handleCreateModalSubmit(v)"
  />
</template>

<style scoped>
.disabled {
  opacity: 0.5;
  cursor: not-allowed !important;
}
</style>
