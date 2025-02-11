<script setup lang="ts">
import { $t } from '@/i18n';
import { ref, watchEffect, type CSSProperties } from 'vue';
import { useRouter } from 'vue-router';
import GenericModal from './GenericModal.vue';

const _LOC_REF_ATTR_MAP = {
  textId: 'data-tekst-text-id',
  textSlug: 'data-tekst-text-slug',
  locId: 'data-tekst-location-id',
  alias: 'data-tekst-location-alias',
  lvl: 'data-tekst-location-level',
  pos: 'data-tekst-location-position',
};

const _LOC_REF_SELECTOR = Object.values(_LOC_REF_ATTR_MAP)
  .map((attr) => `[${attr}]`)
  .join(',');

const props = withDefaults(
  defineProps<{
    html?: string;
    style?: CSSProperties;
  }>(),
  {
    html: '',
  }
);

const emit = defineEmits(['clickLocationRef']);

const router = useRouter();

const domParser = new DOMParser();
const contentRef = ref<HTMLElement>();

// modal state and data
const modalId = ref<string>();
const modalHtml = ref<Record<string, string>>({});
const modalTitles = ref<Record<string, string | undefined>>({});
const showModal = ref(false);

function handleLocationRefClick(e: MouseEvent) {
  e.preventDefault();
  e.stopPropagation();
  emit('clickLocationRef');
  const el = e.target as HTMLElement;
  router.push({
    name: 'browseResolve',
    query: Object.fromEntries(
      Object.entries(_LOC_REF_ATTR_MAP)
        .map(([k, v]) => [k, el.getAttribute(v)])
        .filter(([_, v]) => !!v)
    ),
  });
  window.scrollTo(0, 0);
}

function hydrate(html: string | undefined) {
  if (!html) return undefined;
  // reset state
  modalHtml.value = {};
  modalTitles.value = {};
  modalId.value = undefined;

  const dom = domParser.parseFromString(html, 'text/html');

  // MODALS: iterate modal triggers
  dom.querySelectorAll('[data-tekst-modal-trigger]').forEach((trigger) => {
    if (!(trigger instanceof HTMLElement)) return;
    const currModalId = trigger.getAttribute('data-tekst-modal-trigger');
    if (!currModalId) return;
    // iterate modal content container elements
    dom.querySelectorAll(`[data-tekst-modal="${currModalId}"]`).forEach((modalContent) => {
      // add modal HTML content to modal HTML collection
      modalHtml.value[currModalId] = (modalHtml.value[currModalId] || '') + modalContent.innerHTML;
      // set modal title
      modalTitles.value[currModalId] = modalContent.getAttribute('title') || undefined;
      // remove original modal content element from DOM
      modalContent.remove();
    });
    trigger.addEventListener('click', () => {
      modalId.value = currModalId;
      showModal.value = true;
    });
    trigger.classList.add('modal-trigger');
    trigger.setAttribute(
      'title',
      trigger.getAttribute('title') || $t('general.showAttachmentsAction')
    );
  });

  // INTERNAL LINKS/REFERENCES: iterate internal location links
  dom.querySelectorAll(_LOC_REF_SELECTOR).forEach((el) => {
    if (!(el instanceof HTMLAnchorElement)) return;
    el.removeAttribute('href');
    el.setAttribute('title', $t('browse.location.goTo'));
    el.addEventListener('click', handleLocationRefClick);
    el.classList.add('internal-ref-link');
  });

  // replace content
  contentRef.value?.replaceChildren(...dom.body.children);
}

watchEffect(() => {
  hydrate(props.html);
});
</script>

<template>
  <div ref="contentRef" :style="style"></div>
  <generic-modal
    v-if="Object.keys(modalHtml).length"
    v-model:show="showModal"
    :title="modalId ? modalTitles[modalId] : undefined"
    width="wide"
  >
    <hydrated-html
      :html="modalId ? modalHtml[modalId] : undefined"
      :style="style"
      @click-location-ref="showModal = false"
    />
  </generic-modal>
</template>

<style scoped>
:deep(.modal-trigger) {
  cursor: pointer;
  color: var(--accent-color);
  transition: color 0.2s ease-in-out;
}

:deep(.modal-trigger:hover) {
  color: var(--accent-color-fade1);
}

:deep(a.internal-ref-link) {
  padding: 0 0.2em;
  cursor: pointer;
  border: 1px solid var(--accent-color-fade4);
  border-radius: var(--border-radius);
  font-family: var(--font-family-ui);
  transition: border-color 0.2s ease-in-out;
}

:deep(a.internal-ref-link:hover) {
  color: var(--accent-color);
  border-color: var(--accent-color);
}
</style>
