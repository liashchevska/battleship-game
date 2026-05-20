<template>
  <h1 id="app-title">battleship</h1>
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
#id {
  background-color: transparent;
}
</style>
