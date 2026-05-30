<template>
  <div v-if="shots" :class="[yours ? 'you' : 'opponent', 'board']">
    <div class="board-header text-muted">
      <span class="text-label"> {{ owner }}</span>
      <StatusIndicator v-if="isGameActive" :displayDot="displayDot" :text="state" class="text-state" />
    </div>
    <table class="board-table" :class="[owner, isDisabled ? 'disabled' : 'active']">
      <tbody>
        <tr v-for="(_, x) in rows" :key="x">
          <td v-for="(_, y) in cols" :key="y" class="board-cell">
            <div @click="onCellClick(x, y)" class="board-cell-content">
              &nbsp;
              <div :class="{
                'shot-miss': shots[x][y] == 1,
                'shot-hit': shots[x][y] == 2
              }"></div>
              <div :class="getCellClass(x, y)"></div>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="board-footer">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script>
import { mapActions, mapState } from "vuex";
import { getCellClass as _getCellClass } from "../helpers";
import StatusIndicator from "./StatusIndicator.vue";
import { mapGetters } from "vuex/dist/vuex.cjs.js";

export default {
  components: {
    StatusIndicator,
  },
  props: {
    rows: Number,
    cols: Number,
    ships: Array,
    board: Array,
    shots: Array,

    state: String,
    owner: String,

    yours: Boolean,
    waiting: Boolean,
    displayDot: Boolean,
  },
  computed: {
    ...mapState(["isOver", "opponentLeft", "yourTurn"]),
    ...mapGetters(["isGameActive"]),
    isDisabled() {
      return (
        this.waiting ||
        this.isOver ||
        this.opponentLeft ||
        (!this.yours && !this.yourTurn) ||
        (this.yours && this.yourTurn)
      );
    },
  },
  methods: {
    ...mapActions(["makeMove"]),
    isClickable(x, y) {
      return !this.waiting && !this.yours && this.shots[x][y] == 0;
    },
    onCellClick(x, y) {
      if (this.isClickable(x, y)) {
        this.makeMove({ x: x, y: y })
      }
    },
    getCellClass(x, y) {
      return _getCellClass(this.board, this.ships, x, y)
    }
  }
};
</script>

<style lang="scss">
@use '@/assets/scss/variables';

.board {
  display: flex;
  flex-direction: column;
  gap: variables.$gap-sm
}

.board-header {
  display: flex;
  justify-content: space-between;
}

.board-footer {
  display: flex;
  justify-content: center;

  & .btn {
    flex: 0.5;
  }

}
</style>