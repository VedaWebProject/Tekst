import { type Component } from 'vue';
import PlainTextContentFormItems from '@/forms/resources/contents/PlainTextContentFormItems.vue';
import RichTextContentFormItems from '@/forms/resources/contents/RichTextContentFormItems.vue';
import TextAnnotationContentFormItems from '@/forms/resources/contents/TextAnnotationContentFormItems.vue';

const resourceContentFormItems: Record<string, Component> = {
  plainText: PlainTextContentFormItems,
  richText: RichTextContentFormItems,
  textAnnotation: TextAnnotationContentFormItems,
};

export default resourceContentFormItems;
