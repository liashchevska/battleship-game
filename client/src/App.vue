<template>
  <h1 class="app-title">battleship</h1>
  <router-view />
</template>

<script>
export default {
  mounted() {
    document.documentElement.classList.add("theme-dark");
  }
};
</script>

<style lang="scss">
.app-title {
  text-align: center;
}
</style>
