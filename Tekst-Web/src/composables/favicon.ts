import { watch } from 'vue';
import { useLogo } from '@/composables/logo';

export function useFavicon() {
  const { faviconIco, faviconPng } = useLogo();

  const applyIcon = (iconUrl: string) => {
    const faviconEls = document?.head.querySelectorAll<HTMLLinkElement>(`link[href*="${iconUrl}"]`);
    if (!faviconEls || faviconEls.length === 0) {
      const link = document?.createElement('link');
      const type = iconUrl.endsWith('.ico') ? 'x-icon' : 'png';
      if (link) {
        link.rel = 'icon';
        link.href = iconUrl;
        link.type = `image/${type}`;
        document?.head.append(link);
      }
      return;
    }
    faviconEls?.forEach((el) => (el.href = iconUrl));
  };

  watch(
    [faviconIco, faviconPng],
    ([nIco, nPng], [oIco, oPng]) => {
      if (typeof nIco === 'string' && nIco !== oIco) applyIcon(nIco);
      if (typeof nPng === 'string' && nPng !== oPng) applyIcon(nPng);
    },
    { immediate: true }
  );
}