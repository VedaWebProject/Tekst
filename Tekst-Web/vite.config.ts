import { dirname, resolve } from 'node:path';
import { fileURLToPath, URL } from 'node:url';

import VueI18nPlugin from '@intlify/unplugin-vue-i18n/vite';
import vue from '@vitejs/plugin-vue';
import { visualizer } from 'rollup-plugin-visualizer';
import { defineConfig, PluginOption } from 'vite';

// https://vitejs.dev/config/
export default defineConfig({
  envPrefix: 'TEKST_',
  appType: 'spa',
  server: {
    host: '127.0.0.1',
  },
  plugins: [
    vue(),
    VueI18nPlugin({
      include: resolve(dirname(fileURLToPath(import.meta.url)), './translations/ui/**'),
    }),
    visualizer() as PluginOption,
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  define: {
    __VUE_PROD_DEVTOOLS__: false,
    __VUE_I18N_FULL_INSTALL__: false,
    __VUE_I18N_LEGACY_API__: false,
    __INTLIFY_PROD_DEVTOOLS__: false,
  },
  build: {
    rollupOptions: {
      output: {
        assetFileNames: 'assets/[ext]/[ext]-[hash][extname]',
        chunkFileNames: 'assets/js/chunk-[hash].js',
      },
    },
    chunkSizeWarningLimit: 1200,
  },
});
