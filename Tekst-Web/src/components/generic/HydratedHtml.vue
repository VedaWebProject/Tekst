<script setup lang="ts">
import { $t } from '@/i18n';
import { onMounted, ref, watch, type CSSProperties } from 'vue';
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

const contentRef = ref<HTMLElement | null>(null);

// modal
const modalId = ref<string>();
const modalHtml = ref<Record<string, string | undefined>>({});
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

function hydrate() {
  // reset state
  modalHtml.value = {};
  modalTitles.value = {};
  modalId.value = undefined;

  // MODALS: iterate modal triggers
  contentRef.value?.querySelectorAll('[data-tekst-modal-trigger]').forEach((trigger) => {
    if (!(trigger instanceof HTMLElement)) return;
    const currModalId = trigger.getAttribute('data-tekst-modal-trigger');
    if (!currModalId) return;
    // iterate modal content container elements
    contentRef.value
      ?.querySelectorAll(`[data-tekst-modal="${currModalId}"]`)
      .forEach((modalContent) => {
        // add modal HTML content to modal HTML collection
        modalHtml.value[currModalId] =
          (modalHtml.value[currModalId] || '') + modalContent.innerHTML;
        // set modal title
        modalTitles.value[currModalId] =
          modalContent.getAttribute('title') || trigger.textContent || undefined;
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
  contentRef.value?.querySelectorAll(_LOC_REF_SELECTOR).forEach((el) => {
    if (!(el instanceof HTMLElement)) return;
    // remove href attr if this is an anchor element
    if (el instanceof HTMLAnchorElement) {
      el.removeAttribute('href');
    }
    el.style.cursor = 'pointer';
    el.setAttribute('title', $t('browse.location.goTo'));
    el.classList.add('ui-font');
    el.addEventListener('click', handleLocationRefClick);
  });
}

watch(() => props.html, hydrate);
onMounted(hydrate);
</script>

<template>
  <div ref="contentRef" v-bind="$attrs" v-html="html" :style="style"></div>
  <generic-modal
    v-if="Object.keys(modalHtml).length"
    v-model:show="showModal"
    :title="modalId && modalTitles[modalId]"
    width="wide"
  >
    <hydrated-html :html="modalId && modalHtml[modalId]" :style="style" @click-location-ref="showModal = false"/>
  </generic-modal>
</template>

<style scoped>
:deep(.modal-trigger) {
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: background-color 0.2s ease-in-out;
}

:deep(.modal-trigger:hover) {
  background-color: var(--accent-color-fade5);
}
</style>
