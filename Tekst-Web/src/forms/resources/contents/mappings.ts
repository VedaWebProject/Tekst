import ApiCallContentFormItems from '@/forms/resources/contents/ApiCallContentFormItems.vue';
import AudioContentFormItems from '@/forms/resources/contents/AudioContentFormItems.vue';
import ExternalReferencesContentFormItems from '@/forms/resources/contents/ExternalReferencesContentFormItems.vue';
import ImagesContentFormItems from '@/forms/resources/contents/ImagesContentFormItems.vue';
import LocationMetadataContentFormItems from '@/forms/resources/contents/LocationMetadataContentFormItems.vue';
import PlainTextContentFormItems from '@/forms/resources/contents/PlainTextContentFormItems.vue';
import RichTextContentFormItems from '@/forms/resources/contents/RichTextContentFormItems.vue';
import TextAnnotationContentFormItems from '@/forms/resources/contents/TextAnnotationContentFormItems.vue';
import { type Component } from 'vue';

const resourceContentFormItems: Record<string, Component> = {
  plainText: PlainTextContentFormItems,
  richText: RichTextContentFormItems,
  textAnnotation: TextAnnotationContentFormItems,
  locationMetadata: LocationMetadataContentFormItems,
  audio: AudioContentFormItems,
  images: ImagesContentFormItems,
  externalReferences: ExternalReferencesContentFormItems,
  apiCall: ApiCallContentFormItems,
};

export default resourceContentFormItems;
