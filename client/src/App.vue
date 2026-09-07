<template>
  <div class="app-content">
    <h1 class="app-title">battleship</h1>
    <router-view />
  </div>
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
  font-family: 'Cutive Mono', monospace;
  text-align: center;
  font-size: 1.5rem;
  font-weight: 600;
  letter-spacing: 0.15em;
  line-height: 1;
  transform: scaleY(0.9);
  opacity: 0.9;
  margin: var(--gap-sm) 0;
}

.app-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--gap-md) 0;
}
</style>
