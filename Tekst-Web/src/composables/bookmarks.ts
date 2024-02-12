import { ref } from 'vue';
import { DELETE, GET, POST } from '@/api';
import type { BookmarkRead } from '@/api';
import { useAuthStore } from '@/stores';
import { watchEffect } from 'vue';
import { useMessages } from './messages';
import { $t } from '@/i18n';

const bookmarks = ref<BookmarkRead[]>([]);
const lastUserId = ref<string>();

export function useBookmarks() {
  const auth = useAuthStore();
  const { message } = useMessages();

  async function loadBookmarks() {
    if (auth.user?.id) {
      const { data, error } = await GET('/bookmarks', {});
      if (!error) {
        bookmarks.value = data;
      } else {
        bookmarks.value = [];
      }
    }
  }

  async function createBookmark(locationId: string, comment: string) {
    const { error } = await POST('/bookmarks', {
      body: {
        locationId,
        comment,
      },
    });
    if (!error) {
      await loadBookmarks();
      message.success($t('browse.bookmarks.createSuccess'));
    }
  }

  async function deleteBookmark(id: string) {
    const { error } = await DELETE('/bookmarks/{id}', {
      params: { path: { id } },
    });
    if (!error) {
      bookmarks.value = bookmarks.value.filter((b) => b.id !== id);
      message.success($t('browse.bookmarks.deleteSuccess'));
    } else {
      auth.logout();
    }
  }

  watchEffect(() => {
    if (auth.loggedIn && auth.user?.id !== lastUserId.value) {
      lastUserId.value = auth.user?.id;
      loadBookmarks();
    }
  });

  return { bookmarks, loadBookmarks, createBookmark, deleteBookmark };
}
