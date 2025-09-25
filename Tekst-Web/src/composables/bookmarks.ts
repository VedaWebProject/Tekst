import type { BookmarkRead } from '@/api';
import { DELETE, GET, POST } from '@/api';
import { $t } from '@/i18n';
import { useAuthStore, useStateStore } from '@/stores';
import { computed, ref } from 'vue';
import { useMessages } from './messages';

const allBookmarks = ref<BookmarkRead[] | null>(null);

export function useBookmarks() {
  const state = useStateStore();
  const auth = useAuthStore();
  const { message } = useMessages();

  const bookmarks = computed<BookmarkRead[]>(
    () => allBookmarks.value?.filter((b) => b.textId === state.text?.id) || []
  );

  async function loadBookmarks() {
    if (!!auth.user && allBookmarks.value === null) {
      const { data, error } = await GET('/browse/bookmarks', {});
      if (!error) {
        allBookmarks.value = data;
      } else {
        allBookmarks.value = null;
      }
    }
  }

  async function createBookmark(locationId: string, comment: string) {
    const { data, error } = await POST('/browse/bookmarks', {
      body: {
        locationId,
        comment,
      },
    });
    if (!error) {
      allBookmarks.value?.push(data);
      message.success($t('browse.bookmarks.createSuccess'));
    }
  }

  async function deleteBookmark(id: string) {
    const { error } = await DELETE('/browse/bookmarks/{id}', {
      params: { path: { id } },
    });
    if (!error) {
      allBookmarks.value = allBookmarks.value?.filter((b) => b.id !== id) || null;
      message.success($t('browse.bookmarks.deleteSuccess'));
    }
  }

  return { bookmarks, loadBookmarks, createBookmark, deleteBookmark };
}
