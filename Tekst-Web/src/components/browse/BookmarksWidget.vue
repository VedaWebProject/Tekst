<script setup lang="ts">
import { POST, DELETE, type BookmarkRead } from '@/api';
import { usePlatformData } from '@/composables/platformData';
import { AddIcon, BookmarkFilledIcon, BookmarkIcon } from '@/icons';
import { useAuthStore, useBrowseStore, useStateStore } from '@/stores';
import type { PromptModalProps } from '@/types';
import { NIcon, NDropdown, NButton, type DropdownOption } from 'naive-ui';
import type { VNodeChild } from 'vue';
import { h, computed, type Component, ref } from 'vue';
import { useRouter } from 'vue-router';
import PromptModal from '@/components/generic/PromptModal.vue';
import { $t } from '@/i18n';
import { useMessages } from '@/composables/messages';
import BookmarkOptionLabel from './BookmarkOptionLabel.vue';

defineProps<{
  size?: 'small' | 'medium' | 'large';
  color?: string;
  bgColor?: string;
}>();

const auth = useAuthStore();
const browse = useBrowseStore();
const state = useStateStore();
const { pfData } = usePlatformData();
const { message } = useMessages();
const router = useRouter();

const loading = ref(false);
const promptModalState = ref<PromptModalProps>({});

const bookmarksOptions = computed<DropdownOption[]>(() => {
  const bookmarks = auth.user?.bookmarks || [];
  return [
    {
      label: $t('browse.bookmarks.lblCreate'),
      key: 'create',
      icon: renderIcon(AddIcon),
      action: handleCreateBookmark,
    },
    ...(bookmarks.length
      ? [
          {
            type: 'divider',
            key: 'divider',
          },
          {
            label: `${$t('browse.bookmarks.bookmarks')}: ${state.text?.title}`,
            type: 'group',
            key: 'bookmarksGroup',
            children: [
              ...bookmarks.map((bookmark) => ({
                key: bookmark.locationId,
                bookmark: bookmark,
                show: bookmark.textId === state.text?.id,
                icon: renderIcon(BookmarkIcon),
                action: () => handleBookmarkSelect(bookmark),
              })),
            ],
          },
        ]
      : []),
  ];
});

function renderOptionLabel(o: DropdownOption): VNodeChild {
  if (!o.bookmark) {
    return o.label as VNodeChild;
  }
  const bookmark = o.bookmark as BookmarkRead;
  return h(BookmarkOptionLabel, {
    bookmark,
    levelLabel: state.textLevelLabels[bookmark.level],
    onDelete: () => handleDeleteBookmark(bookmark.id),
  });
}

async function handleDeleteBookmark(bookmarkId: string) {
  const { error } = await DELETE('/bookmarks/{id}', {
    params: { path: { id: bookmarkId } },
  });
  if (!error) {
    if (auth.user) {
      auth.user.bookmarks = auth.user.bookmarks?.filter((b) => b.id !== bookmarkId);
    }
    message.success($t('browse.bookmarks.deleteSuccess'));
  } else {
    message.error($t('errors.unexpected'), error);
  }
}

function handleCreateBookmark() {
  if (auth.user?.bookmarks?.find((b) => b.locationId === browse.locationPathHead?.id)) {
    message.error($t('browse.bookmarks.errorBookmarkExists'));
    return;
  }
  promptModalState.value = {
    show: true,
    actionKey: 'createBookmark',
    initialValue: '',
    title: $t('browse.bookmarks.commentModalTitle'),
    inputLabel: $t('browse.bookmarks.commentModalInputLabel'),
  };
}

async function handleCreateModalSubmit(comment: string) {
  loading.value = true;
  const { data, error, response } = await POST('/bookmarks', {
    body: {
      locationId: browse.locationPathHead?.id || '',
      comment,
    },
  });
  if (!error) {
    auth.user?.bookmarks?.push(data);
    message.success(
      $t('browse.bookmarks.createSuccess', { locationLabel: browse.locationPathHead?.label })
    );
  } else if (response.status == 409) {
    message.error($t('browse.bookmarks.errorBookmarkExists'));
  } else {
    message.error($t('errors.unexpected'), error);
  }
  loading.value = false;
}

async function handleBookmarkSelect(bookmark: BookmarkRead) {
  router.replace({
    name: 'browse',
    params: { text: pfData.value?.texts.find((t) => t.id === bookmark.textId)?.slug || '' },
    query: { lvl: bookmark.level, pos: bookmark.position },
  });
}

function renderIcon(icon: Component) {
  return () => h(NIcon, null, { default: () => h(icon) });
}

function handleActionSelect(o: DropdownOption & { action?: () => void }) {
  o.action?.();
}
</script>

<template>
  <n-dropdown
    :options="bookmarksOptions"
    :render-label="renderOptionLabel"
    to="#app-container"
    trigger="click"
    @select="(_, o) => handleActionSelect(o)"
  >
    <n-button
      :size="size"
      :color="bgColor"
      :style="{ color: color }"
      :focusable="false"
      :title="$t('browse.bookmarks.bookmarks')"
      :disabled="loading"
      :loading="loading"
    >
      <template #icon>
        <n-icon :component="BookmarkFilledIcon" />
      </template>
    </n-button>
  </n-dropdown>

  <PromptModal
    v-bind="promptModalState"
    @submit="(_, v) => handleCreateModalSubmit(v)"
    @update:show="promptModalState.show = $event"
    @after-leave="promptModalState = {}"
  />
</template>
