<template>
  <div v-if="shots" :class="[yours ? 'you' : 'opponent', 'board']">
    <h3 class="board-owner">{{ owner }} </h3>
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
  </div>
</template>

<script>
import { mapActions, mapState } from "vuex";
import { getCellClass as _getCellClass } from "../helpers";

export default {
  props: {
    rows: Number,
    cols: Number,
    ships: Array,
    board: Array,
    shots: Array,
    yours: Boolean,

    waiting: Boolean
  },
  computed: {
    ...mapState(["isOver", "opponentLeft", "yourTurn"]),
    isDisabled() {
      return (
        this.waiting ||
        this.isOver ||
        this.opponentLeft ||
        (!this.yours && !this.yourTurn) ||
        (this.yours && this.yourTurn)
      );
    },
    isActive() {
      return !(this.waiting || this.isOver || this.opponentLeft);
    },
    owner() {
      return this.yours ? 'you' : 'opponent'
    },
    status() {
      return ''
    }
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
