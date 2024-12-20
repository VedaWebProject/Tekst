<script setup lang="ts">
import { $t } from '@/i18n';
import { onMounted, ref, watch, type CSSProperties } from 'vue';
import GenericModal from './GenericModal.vue';

const props = withDefaults(
  defineProps<{
    html?: string;
    style?: CSSProperties;
  }>(),
  {
    html: '',
  }
);

const contentRef = ref<HTMLElement | null>(null);

// modal
const modalId = ref<string>();
const modalHtml = ref<Record<string, string | undefined>>({});
const modalTitles = ref<Record<string, string | undefined>>({});
const showModal = ref(false);

function hydrate() {
  // reset state
  modalHtml.value = {};
  modalTitles.value = {};
  modalId.value = undefined;
  // MODALS
  // iterate modal triggers
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
    // add click listener to trigger
    trigger.addEventListener('click', () => {
      modalId.value = currModalId;
      showModal.value = true;
    });
    // style trigger
    trigger.style.cursor = 'pointer';
    // set trigger title attribute
    trigger.setAttribute(
      'title',
      trigger.getAttribute('title') || $t('general.showAttachmentsAction')
    );
  });
}

watch(() => props.html, hydrate);
onMounted(hydrate);
</script>

<template>
  <div ref="contentRef" v-html="html" :style="style"></div>
  <generic-modal
    v-if="Object.keys(modalHtml).length"
    v-model:show="showModal"
    :title="modalId && modalTitles[modalId]"
  >
    <div v-html="modalId && modalHtml[modalId]" :style="style"></div>
  </generic-modal>
</template>
