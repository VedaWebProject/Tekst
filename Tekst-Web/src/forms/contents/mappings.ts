import { type Component } from 'vue';
import PlaintextFormItems from '@/forms/contents/PlaintextFormItems.vue';

const resourceContentFormItems: Record<string, Component> = {
  plaintext: PlaintextFormItems,
};

export default resourceContentFormItems;
