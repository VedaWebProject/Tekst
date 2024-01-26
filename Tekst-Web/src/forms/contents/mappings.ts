import { type Component } from 'vue';
import PlainTextFormItems from '@/forms/contents/PlainTextFormItems.vue';

const resourceContentFormItems: Record<string, Component> = {
  plainText: PlainTextFormItems,
};

export default resourceContentFormItems;
