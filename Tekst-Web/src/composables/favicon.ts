import { useLogo } from '@/composables/logo';
import { watch } from 'vue';

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
      if (!!nIco && nIco !== oIco) applyIcon(nIco);
      if (!!nPng && nPng !== oPng) applyIcon(nPng);
    },
    { immediate: true }
  );
}
