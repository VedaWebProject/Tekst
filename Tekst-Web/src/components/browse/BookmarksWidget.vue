<script setup lang="ts">
import { type BookmarkRead } from '@/api';
import GenericModal from '@/components/generic/GenericModal.vue';
import PromptModal from '@/components/generic/PromptModal.vue';
import LocationLabel from '@/components/LocationLabel.vue';
import { useBookmarks } from '@/composables/bookmarks';
import { useMessages } from '@/composables/messages';
import { usePlatformData } from '@/composables/platformData';
import { bookmarkFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { AddIcon, BookIcon, BookmarksIcon, DeleteIcon, SearchIcon } from '@/icons';
import { useBrowseStore, useStateStore } from '@/stores';
import { NButton, NFlex, NIcon, NInput, NList, NListItem, NThing } from 'naive-ui';
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';

defineProps<{
  buttonSize?: 'small' | 'medium' | 'large';
}>();

const browse = useBrowseStore();
const state = useStateStore();
const { pfData } = usePlatformData();
const { message } = useMessages();
const { bookmarks, loadBookmarks, createBookmark, deleteBookmark } = useBookmarks();
const router = useRouter();

const filterString = ref<string>();
const filteredBookmarks = computed(() =>
  !filterString.value
    ? bookmarks.value
    : bookmarks.value.filter((b) =>
        [b.comment, ...b.locationLabels]
          .join(' ')
          .toLowerCase()
          .includes(filterString.value?.toLowerCase() || ':(')
      )
);

const showModal = ref(false);
const promptModalRef = ref();
const loading = ref(false);

const maxCountReached = computed(() => bookmarks.value.length >= 1000);
const bookmarkAlreadyExists = computed(
  () => !!bookmarks.value.find((b) => b.locationId === browse.locationPathHead?.id)
);

async function handleDeleteBookmark(bookmarkId: string) {
  loading.value = true;
  await deleteBookmark(bookmarkId);
  loading.value = false;
}

function handleCreateBookmarkClick() {
  if (loading.value || maxCountReached.value) {
    return;
  }
  if (bookmarkAlreadyExists.value) {
    message.error($t('errors.bookmarkExists'));
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
    params: {
      textSlug: pfData.value?.texts.find((t) => t.id === bookmark.textId)?.slug || '',
      locId: bookmark.locationId,
    },
  });
}

async function handleWidgetClick() {
  showModal.value = true;
  loading.value = true;
  await loadBookmarks();
  loading.value = false;
}
</script>

<template>
  <n-button
    type="primary"
    :size="buttonSize"
    :focusable="false"
    :title="$t('browse.bookmarks.bookmarks')"
    :bordered="false"
    @click.stop.prevent="handleWidgetClick"
  >
    <template #icon>
      <n-icon :component="BookmarksIcon" />
    </template>
  </n-button>

  <generic-modal
    v-model:show="showModal"
    width="wide"
    :title="$t('browse.bookmarks.bookmarks')"
    :icon="BookmarksIcon"
  >
    <n-input
      v-model:value="filterString"
      :placeholder="$t('search.searchAction')"
      round
      clearable
      class="my-md"
    >
      <template #prefix>
        <n-icon :component="SearchIcon" />
      </template>
    </n-input>

    <n-list hoverable clickable style="background-color: transparent">
      <n-list-item
        :class="{ disabled: loading || maxCountReached || bookmarkAlreadyExists }"
        @click="handleCreateBookmarkClick"
      >
        <n-thing content-indented>
          <template #avatar>
            <n-icon :component="AddIcon" size="large" />
          </template>
          <span v-if="!maxCountReached">
            {{ $t('browse.bookmarks.lblCreate') }}
          </span>
          <span v-else>{{ $t('browse.bookmarks.maxCountReached') }}</span>
        </n-thing>
      </n-list-item>

      <n-list-item
        v-for="bookmark in filteredBookmarks"
        :key="bookmark.id"
        @click="handleBookmarkSelect(bookmark)"
      >
        <n-thing
          :content-indented="!state.smallScreen"
          description-style="font-size: var(--font-size-tiny)"
        >
          <template v-if="!state.smallScreen" #avatar>
            <n-icon :component="BookIcon" size="large" />
          </template>
          <template #header>
            <location-label :location-labels="bookmark.locationLabels" />
          </template>
          <template #header-extra>
            <n-flex align="center" style="height: 100%">
              <n-button
                secondary
                size="small"
                :focusable="false"
                :disabled="loading"
                :loading="loading"
                :title="$t('general.deleteAction')"
                @click.stop.prevent="handleDeleteBookmark(bookmark.id)"
              >
                <template #icon>
                  <n-icon :component="DeleteIcon" />
                </template>
              </n-button>
            </n-flex>
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
    type="textarea"
    action-key="createBookmark"
    :title="$t('browse.bookmarks.commentModalTitle')"
    :icon="BookmarksIcon"
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
