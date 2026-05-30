<template>
  <h2 class="game-status">
    <!-- <span class="text-label"> game status: </span> -->
    <div class="state">
      <StatusIndicator :class="currentStatus.code" :displayDot="!isGameActive" :text="currentStatus.text" />
      <ThreeDots v-if="this.waiting" />
    </div>

    <!-- <div class="status-right"> -->
    <span class="text-state btn-text" @click="leaveGame">[leave game]</span>
    <!-- </div> -->
    <!-- <span class="text-label"> {{ currentStatus }}</span> -->
  </h2>
</template>

<script>
import { mapGetters, mapState } from "vuex";
import ThreeDots from "./ThreeDots.vue";
import StatusIndicator from "./StatusIndicator.vue";
import { mapActions } from "vuex/dist/vuex.cjs.js";
export default {
  components: {
    ThreeDots,
    StatusIndicator
  },
  props: {
    waiting: Boolean
  },
  computed: {
    ...mapState([
      "yourTurn",
      "isOver",
      "youWon",
      "opponentLeft"
    ]),
    ...mapGetters(['isGameActive']),
    ...mapActions(['leaveGame']),
    currentStatus() {
      if (this.waiting) {
        return { text: 'waiting for an opponent', code: 'wait' }
      }
      if (this.isOver) {
        const result = this.youWon ? 'won' : 'lost'
        return { text: `game over | you ${result}`, code: result }
      }
      if (this.opponentLeft) {
        return { text: 'game over | opponent left', code: 'left' }
      }
      return { text: `${this.yourTurn ? 'your' : "opponent's"} turn`, code: 'turn' }
    },
  }
};
</script>

<style lang="scss">
@use '@/assets/scss/variables';

.game-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: variables.$gap-xs;
}
</style>