import { useLogo } from '@/composables/logo';
import { watchEffect } from 'vue';

export function useFavicon() {
  const { faviconIco, faviconPng } = useLogo();

  const _apply = (url: string) => {
    // check if this is an ICO or PNG
    const isIco = url.endsWith('.ico');
    // delete existing favicon elements
    if (isIco) {
      const sel1 = 'head > link[rel="icon"][type="image/x-icon"]';
      const sel2 = 'head > link[rel="shortcut icon"][type="image/x-icon"]';
      document.head.querySelectorAll<HTMLLinkElement>(`${sel1}, ${sel2}`).forEach((el) => {
        el.remove();
      });
    } else {
      const sel = 'head > link[rel="icon"][type="image/png"]';
      document.head.querySelectorAll<HTMLLinkElement>(sel).forEach((el) => {
        el.remove();
      });
    }
    // create new favicon element
    const link = document.createElement('link');
    link.rel = 'icon';
    link.href = url;
    link.type = isIco ? 'image/x-icon' : 'image/png';
    // append to head
    document.head.append(link);
    // if this is an ICO file, append copy with alternative rel attribute value
    if (isIco) {
      const link2 = link.cloneNode(true) as HTMLLinkElement;
      link2.rel = 'shortcut icon';
      document.head.append(link2);
    }
  };

  watchEffect(() => {
    if (faviconPng.value) _apply(faviconPng.value);
  });

  watchEffect(() => {
    if (faviconIco.value) _apply(faviconIco.value);
  });
}
