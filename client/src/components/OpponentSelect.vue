<template>
  <div class="opponent-select">
    <p class="text-label">Opponent type</p>
    <template v-if="gameId == null">
      <template v-for="opponent in opponents">
        <button @click="createGameWith(opponent)"
          :class="['btn', isSelected(opponent) ? 'btn-primary' : 'btn-secondary']">{{ opponent }}</button>
      </template>
    </template>
    <template v-else>
      <button class="btn btn-primary friend-selected ">friend</button>
    </template>
  </div>
</template>

<script>
import { mapActions, mapState } from "vuex";
export default {
  data() {
    return {
      opponents: ['computer', 'random', 'friend'],
    }
  },
  computed: {
    ...mapState(["gameId", "opponentType"])
  },
  methods: {
    isSelected(opponent) { return opponent === this.opponentType },
    ...mapActions([
      "createGameWith",
    ])
  }
};
</script>

<style lang="scss">
@use '@/assets/scss/variables';

.opponent-select {
  & p {
    margin-top: variables.$gap-md;
    margin-bottom: variables.$gap-sm;
    text-align: center;
    opacity: 0.8;
  }
}
</style>