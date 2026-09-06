<template>
  <h2 class="game-status">
    <div class="state">
      <StatusIndicator :class="currentStatus.code" :displayDot="!isGameActive" :text="currentStatus.text" />
      <ThreeDots v-if="this.waiting" />
    </div>
    <button class="text-state btn-text" @click="leaveGame">[leave game]</button>
  </h2>
</template>

<script>
import { mapGetters, mapState, mapActions } from "vuex";
import ThreeDots from "./ThreeDots.vue";
import StatusIndicator from "./StatusIndicator.vue";

export default {
  components: {
    ThreeDots,
    StatusIndicator
  },
  props: {
    waiting: Boolean
  },
  methods: {
    ...mapActions(['leaveGame']),
  },
  computed: {
    ...mapState([
      "yourTurn",
      "isOver",
      "youWon",
      "opponentLeft"
    ]),
    ...mapGetters(['isGameActive']),
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
.game-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--gap-md);
}
</style>