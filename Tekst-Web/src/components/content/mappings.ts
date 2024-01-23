import { defineAsyncComponent, type Component } from 'vue';

const contentComponents: Record<string, Component> = {
  plaintext: defineAsyncComponent(() => import('@/components/content/PlaintextContent.vue')),
};

export default contentComponents;
