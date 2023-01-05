<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router';
import FullScreenLoader from '@/components/FullScreenLoader.vue';
import LanguageSwitcher from '@/i18n/LanguageSwitcher.vue';
import { onMounted, onBeforeMount } from 'vue';
import { setI18nLanguage } from '@/i18n';
import { useGeneralAppState } from '@/stores/general';

const generalAppState = useGeneralAppState();

onBeforeMount(() => {
  generalAppState.startGlobalLoading();
});

onMounted(() => {
  // TODO: instead of just i18n, all resources needed for bootstrapping the
  // client should be loaded from the server here...
  setI18nLanguage()
    .then(() => {
      generalAppState.finishGlobalLoading();
    })
    .catch((error) => {
      console.error(error);
      // TODO: Give error feedback...
    });
});
</script>

<template>
  <header>
    <img alt="TextRig Logo" class="logo" src="@/assets/logo.png" width="125" height="125" />

    <div class="wrapper">
      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/about">About</RouterLink>
      </nav>

      <h2>{{ $t('foo.welcome') }}</h2>
      <LanguageSwitcher />
    </div>
  </header>

  <RouterView />
  <FullScreenLoader :show="generalAppState.globalLoading" duration="100ms" text="loading..." />
</template>

<style scoped>
.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: #f00;
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid #00f;
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style>
