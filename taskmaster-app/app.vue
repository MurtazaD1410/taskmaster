<script setup lang="ts"></script>

<template>
  <NuxtLayout>
    <UApp :toaster="{ expand: false, duration: 2000 }">
      <NuxtRouteAnnouncer />
      <NuxtPage />
    </UApp>
  </NuxtLayout>
</template>
