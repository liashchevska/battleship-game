<template>
  <div class="modal-wrapper">
    <div class="modal">
      <div>Sorry, this game is unavailable.</div>
      <button @click="resetGame" class="btn-primary modal-button">OK</button>
    </div>
  </div>
</template>

<script>
import { mapActions } from "vuex";
export default {
  methods: {
    ...mapActions(["resetGame"])
  }
};
</script>
