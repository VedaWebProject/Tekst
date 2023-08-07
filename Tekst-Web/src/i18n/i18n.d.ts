/**
 * THIS IS A TEMPORARY WORKAROUND, AS TYPESCRIPT
 * DOESN'T RECOGNIZE THE INJECTION OF TRANSLATE FUNCTIONS.
 * SEE https://github.com/intlify/vue-i18n-next/issues/1403
 */

export {};

declare module 'vue' {
  interface ComponentCustomProperties {
    $t: ComposerTranslation<
      Messages,
      Locales,
      RemoveIndexSignature<{
        [K in keyof DefineLocaleMessage]: DefineLocaleMessage[K];
      }>
    >;
    $tm: Composition['tm'];
  }
}
