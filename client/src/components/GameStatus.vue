<template>
  <div class="game-status">
    game status: {{ currentStatus }}
  </div>
</template>

<script>
import { mapState } from "vuex";
export default {
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
    currentStatus() {
      if (this.waiting) {
        return 'waiting for an opponent'
      }
      if (this.isOver) {
        return `game over | you ${this.youWon ? 'won' : 'lost'}`
      }
      if (this.opponentLeft) {
        return 'game over | opponent left'
      }
      return `${this.yourTurn ? 'your' : "opponent's"} turn`
    },
  }
};
</script>