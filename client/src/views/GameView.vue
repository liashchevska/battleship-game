<template>
  <div class="game-container">
    <GameIsInvalidModal v-if="gameIsInvalid" />

    <template v-if="!shipsPlaced">
      <ShipPlacement :rows="rows" :cols="cols" />
      <div class="actions-panel">
        <OpponentSelect />
        <button class="btn btn-primary" @click="startGame">start game</button>
      </div>
    </template>

    <div v-if="friendAsOpponent && shipsPlaced && !gameStarted">
      <div class="link-for-a-friend">
        send this link to your frined:
        <span @click="copyLink" class="link-itself">{{ link }}</span>
      </div>
    </div>

    <template v-if="shipsPlaced">
      <GameStatus :waiting="!gameStarted && shipsPlaced" />

      <div class="boards">
        <GameBoard :displayDot="!yourTurn" owner="you" :state="yourTurn ? 'waiting' : 'their turn'" :rows="rows"
          :cols="cols" :ships="ships" :board="getBoard(rows, cols, ships)" :shots="shots" :yours="true"
          :waiting="false">
        </GameBoard>

        <GameBoard :displayDot="yourTurn" owner="opponent" :state="yourTurn ? 'your turn' : 'waiting'" :rows="rows"
          :cols="cols" :ships="opponentShips" :board="getBoard(rows, cols, opponentShips)" :shots="opponent"
          :yours="false" :waiting="!gameStarted && shipsPlaced" />

      </div>
    </template>
  </div>
</template>

<script>
import { mapActions, mapState } from "vuex";
import { zeros, getBoard } from "../helpers";
import ShipPlacement from "@/components/ShipPlacement.vue";
import OpponentSelect from "@/components/OpponentSelect.vue";
import GameStatus from "@/components/GameStatus.vue";
import GameBoard from "@/components/GameBoard.vue";
import GameIsInvalidModal from "@/components/GameIsInvalidModal.vue";
import { useClipboard } from '@vueuse/core'

export default {
  components: {
    ShipPlacement,
    GameStatus,
    GameBoard,
    OpponentSelect,
    GameIsInvalidModal
  },

  setup() {
    const { text, copy, copied, isSupported } = useClipboard({
      legacy: true
    })

    return { text, copy, copied, isSupported }
  },
  data() {
    return {
      dummyBoard: [],
    };
  },
  computed: {
    ...mapState([
      "socket",
      "savedGameId",
      "friendAsOpponent",
      "rows",
      "cols",
      "ships",

      "board",
      "shots",
      "opponent",
      "opponentShips",
      "yourTurn",
      "opponentLeft",

      "shipsPlaced",
      "gameStarted",
      "gameId",
      "gameIsInvalid"
    ]),
    link() {
      return document.URL + "join" + this.gameId;
    }
  },
  created() {
    this.dummyBoard = zeros(this.rows, this.cols, 0);
    this.$store.dispatch("initSocket", {
      handler: this.onGameUpdate
    });
    window.addEventListener("beforeunload", this.beforeWindowUnload);
  },

  methods: {
    getBoard,
    ...mapActions([
      "onSocketMessage",
      "updateGame",
      "startGame",
      "leaveGame",
      "resetGame"
    ]),
    beforeWindowUnload(event) {
      if (this.gameStarted && !this.opponentLeft) {
        event.preventDefault();
        event.returnValue = "";
        return null;
      }
    },
    onGameUpdate(event) {
      let data = JSON.parse(event.data);
      this.onSocketMessage(data);
    },
    copyLink() {
      if (this.isSupported) {
        this.copy(this.link);
        alert("Link was copied!");
      }
    }
  }
};
</script>


<style lang="scss">
@use '@/assets/scss/variables';

.game-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: variables.$gap-sm;
}

.boards {
  display: flex;
  flex-direction: column;
  gap: variables.$gap-md;

  // Change min-width
  @media (min-width: 768px) {
    flex-direction: row;
  }
}

.player-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: variables.$gap-md;
}

.actions-panel {
  display: flex;
  flex-direction: column;
  gap: variables.$gap-sm;

}
</style>