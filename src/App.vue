<template>
  <div id="app" class="bg-gray-50 min-h-screen">
    <Header v-if="!isAuthPage" />
    <div class="w-full pt-20 pb-6" v-if="!isAuthPage">
      <Sidebar />
      <main class="w-full ml-64">
        <router-view />
      </main>
    </div>
    <router-view v-if="isAuthPage" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Header from './components/Header.vue'
import Sidebar from './components/Sidebar.vue'

const route = useRoute()

const isAuthPage = computed(() => {
  return route.path === '/login' || route.path === '/register'
})
</script>

<style scoped>
#app {
  min-height: 100vh;
}
</style>
