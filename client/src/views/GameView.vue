<template>
  <div class="game-container">
    <GameIsInvalidModal v-if="gameIsInvalid" />

    <div class="lobby-view" v-if="!shipsPlaced">
      <ShipPlacement :rows="rows" :cols="cols" />
      <div class="actions-panel">
        <OpponentSelect />
        <button class="btn btn-primary" @click="startGame">start game</button>
      </div>
    </div>

    <div v-if="friendAsOpponent && shipsPlaced && !gameStarted" class="join-link">
      <span class="link-text text-state">send this link to your frined:</span>
      <span @click="copyLink" class="text-label link-itself">{{ link }}</span>
    </div>

    <div class="game-view" v-if="shipsPlaced">
      <GameStatus :waiting="!gameStarted && shipsPlaced" />

      <div class="boards">
        <GameBoard :displayDot="!yourTurn" owner="you" :state="yourTurn ? 'waiting' : 'their turn'" :rows="rows"
          :cols="cols" :ships="ships" :board="getBoard(rows, cols, ships)" :shots="shots" :yours="true"
          :waiting="false" />

        <GameBoard :displayDot="yourTurn" owner="opponent" :state="yourTurn ? 'your turn' : 'waiting'" :rows="rows"
          :cols="cols" :ships="opponentShips" :board="getBoard(rows, cols, opponentShips)" :shots="opponent"
          :yours="false" :waiting="!gameStarted && shipsPlaced" />

      </div>
      <button class="text-state btn-text" @click="leaveGame">[leave game]</button>
    </div>
  </div>
</template>

<script>
import { mapActions, mapState, mapGetters } from "vuex";
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
    ...mapGetters([
      'friendAsOpponent',
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
@use '@/assets/scss/mixins';

.game-container {
  display: flex;
  flex-direction: column;

  align-items: center;
  min-height: 0;

  margin: var(--gap-sm);
}

.game-view {
  margin-top: var(gap-xs);
  display: flex;
  flex-direction: column;
  gap: var(--gap-md);

  @media (min-width: variables.$boards-breakpoint) {
    gap: var(--gap-lg);
  }
}

.lobby-view {
  display: flex;
  flex-direction: column;
  gap: var(--gap-sm);
}

.boards {
  display: flex;
  flex-direction: column;
  // gap: var(--gap-xs);

  @media (min-width: variables.$boards-breakpoint) {
    flex-direction: row;
    gap: var(--gap-lg);
  }
}

.player-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--gap-md);
}

.actions-panel {
  display: flex;
  flex-direction: column;
  gap: var(--gap-sm);
  padding-bottom: var(--gap-md);
}

.join-link {
  display: flex;
  flex-direction: column;
  align-items: center;

  @media (min-width: variables.$boards-breakpoint) {
    flex-direction: row;
  }

}

.link-itself {
  opacity: 0.85;

  @include mixins.themify using ($theme-map) {
    color: mixins.theme-based($theme-map, "opponent");
  }

  &:hover {
    cursor: pointer;
    opacity: 1;
  }
}
</style>