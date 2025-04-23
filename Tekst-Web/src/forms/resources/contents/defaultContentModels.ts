export const defaultContentModels = {
  plainText: {
    text: '',
  },
  richText: {
    html: '',
  },
  textAnnotation: {
    tokens: [
      {
        token: undefined,
        annotations: [],
      },
    ],
  },
  locationMetadata: {
    entries: [
      {
        key: undefined,
        value: undefined,
      },
    ],
  },
  audio: {
    files: [
      {
        url: undefined,
        caption: undefined,
      },
    ],
  },
  images: {
    files: [
      {
        url: '',
        thumbUrl: undefined,
        sourceUrl: undefined,
        caption: undefined,
      },
    ],
  },
  externalReferences: {
    links: [
      {
        url: undefined,
        title: undefined,
        description: undefined,
      },
    ],
  },
  apiCall: {
    url: undefined,
  },
};
