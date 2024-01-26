import { defineAsyncComponent, type Component } from 'vue';

const contentComponents: Record<string, Component> = {
  plainText: defineAsyncComponent(() => import('@/components/content/PlainTextContent.vue')),
  richText: defineAsyncComponent(() => import('@/components/content/RichTextContent.vue')),
};

export default contentComponents;
