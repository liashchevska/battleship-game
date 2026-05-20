<template>
  <div class="game-status">
    <h2 v-if="!waiting && !isOver && !opponentLeft" :class="[
      !waiting && yourTurn ? 'status-your-turn' : 'status-opponents-turn '
    ]">
      It's {{ yourTurn ? "your" : "opponents's" }} turn.
    </h2>
    <h2 v-if="waiting" class="status-waiting">waiting for an opponent</h2>
    <h2 v-if="isOver" :class="youWon ? 'status-you-won' : 'status-you-lost'">
      Game over. You {{ youWon ? "won!" : "lost!" }}
    </h2>
    <h2 v-if="opponentLeft && !isOver" class="status-opponent-left">
      Opponent has left the game.
    </h2>
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
      "shipsPlaced",
      "gameStarted",
      "yourTurn",
      "isOver",
      "youWon",
      "opponentLeft"
    ])
  }
};
</script>
