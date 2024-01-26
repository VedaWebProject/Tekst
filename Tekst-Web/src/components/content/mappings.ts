import { defineAsyncComponent, type Component } from 'vue';

const contentComponents: Record<string, Component> = {
  plainText: defineAsyncComponent(() => import('@/components/content/PlainTextContent.vue')),
};

export default contentComponents;
