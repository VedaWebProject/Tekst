import vueI18n from '@intlify/eslint-plugin-vue-i18n';
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting';
import vueTsEslintConfig from '@vue/eslint-config-typescript';
import pluginVue from 'eslint-plugin-vue';

export default [
  {
    name: 'app/files-to-lint',
    files: ['**/*.{ts,mts,tsx,vue,js,jsx,cjs,mjs,cts}'],
  },

  {
    name: 'app/files-to-ignore',
    ignores: ['**/dist/**', '**/dist-ssr/**', '**/coverage/**'],
  },

  ...pluginVue.configs['flat/essential'],
  ...vueTsEslintConfig(),
  skipFormatting,

  ...vueI18n.configs['flat/recommended'],
  {
    rules: {
      '@intlify/vue-i18n/no-raw-text': 'off',
      '@intlify/vue-i18n/no-unused-keys': 'off',
    },
    settings: {
      'vue-i18n': {
        localeDir: {
          pattern: './translations/ui/*.yml', // extension is glob formatting!
          localeKey: 'file', // or 'path' or 'key'
        },
        // Specify the version of `vue-i18n` you are using.
        // If not specified, the message will be parsed twice.
        messageSyntaxVersion: '^10.0.1',
      },
    },
  },
];
