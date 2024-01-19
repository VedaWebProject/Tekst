import { defineAsyncComponent, type Component } from 'vue';

const contentComponents: Record<string, Component> = {
  plaintext: defineAsyncComponent(
    () => import('@/components/browse/contents/PlaintextContent.vue')
  ),
};

export default contentComponents;
