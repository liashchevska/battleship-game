<template>
  <div v-if="board" class="board ship-placement">

    <div class="placement-tips">
      <p class="">Placement tips:</p>
      <ul>
        <li>Drag and drop ships to reposition them on the grid</li>
        <li>Click a ship cell to rotate the ship clockwise around that cell</li>
      </ul>
    </div>

    <table class="board-table">
      <circles-to-rhombuses-spinner v-if="loading" :animation-duration="2500" :rhombus-size="15" :color="'#38bdf8'" />
      <tbody>
        <tr v-for="(_, row) in rows" :key="row">
          <td v-for="(_, col) in cols" :key="col" class="board-cell">
            <div class="board-cell-content" @drop="onDrop($event, row, col)" @dragenter.prevent @dragover.prevent>
              &nbsp;
              <div v-if="board[row][col] !== -1" :class="getCellClass(row, col)" draggable="true"
                @dragstart="onDragStart($event, board[row][col])" @click="rotate($event, board[row][col])">
              </div>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <button class="btn btn-secondary" @click="randomizeShips">randomize ships</button>
  </div>
</template>

<script>
import { mapActions, mapState } from "vuex";
import { CirclesToRhombusesSpinner } from "epic-spinners";

import {
  getBoard,
  getCellClass as _getCellClass,
  getClicked,
  getDifference,
  getNewOrientation,
  getOffset,
  getTempShipsAndNewShip,
  isPlacementPossible,
  placeShips,
  rotateMatrix,
  zeros,
} from "../helpers";

export default {
  props: {
    rows: Number,
    cols: Number,
  },
  components: {
    CirclesToRhombusesSpinner,
  },
  computed: {
    ...mapState(["ships", "loading"]),
    board() {
      return getBoard(this.rows, this.cols, this.ships);
    },
  },
  methods: {
    ...mapActions(["randomizeShips"]),
    getCellClass(row, col) {
      return _getCellClass(this.board, this.ships, row, col)
    },
    onDragStart(event, shipIndex) {
      event.dataTransfer.dropEffect = "move";
      event.dataTransfer.effectAllowed = "move";

      let [offsetRow, offsetCol] = getOffset(event);

      event.dataTransfer.setData("shipIndex", shipIndex);
      event.dataTransfer.setData("offsetRow", offsetRow);
      event.dataTransfer.setData("offsetCol", offsetCol);
    },
    onDrop(event, x, y) {
      let shipIndex = event.dataTransfer.getData("shipIndex");
      let offsetRow = parseInt(event.dataTransfer.getData("offsetRow"));
      let offsetCol = parseInt(event.dataTransfer.getData("offsetCol"));

      let newX = x - offsetRow;
      let newY = y - offsetCol;

      let [tempShips, ship] = getTempShipsAndNewShip(this.ships, shipIndex);
      ship.x = newX;
      ship.y = newY;

      let currentBoard = placeShips(this.rows, this.cols, tempShips);
      if (isPlacementPossible(currentBoard, ship, this.rows, this.cols)) {
        this.ships[shipIndex] = ship;
      }
    },
    rotate(event, shipIndex) {
      if (this.ships[shipIndex].length == 1) {
        return;
      }

      let [offsetRow, offsetCol] = getOffset(event);
      let [tempShips, ship] = getTempShipsAndNewShip(this.ships, shipIndex);

      let clickedX = getClicked(this.ships[shipIndex].x, offsetRow);
      let clickedY = getClicked(this.ships[shipIndex].y, offsetCol);

      let diffRow = getDifference(ship.rows, offsetRow);
      let diffCol = getDifference(ship.cols, offsetCol);
      let maxDiff = Math.max(diffRow, diffCol);

      let size = maxDiff * 2 + 1;

      let centerTemp = Math.floor(size / 2);
      let x = centerTemp - offsetRow;
      let y = centerTemp - offsetCol;

      let shipMatrix = zeros(size, size, 0);
      for (let i = x; i < x + ship.rows; i++) {
        for (let j = y; j < y + ship.cols; j++) {
          shipMatrix[i][j] = 1;
        }
      }

      let initX = clickedX - maxDiff;
      let initY = clickedY - maxDiff;

      let newX, newY;
      let rotated = rotateMatrix(shipMatrix);
      for (let i = 0; i < size; i++) {
        for (let j = 0; j < size; j++) {
          if (rotated[i][j] == 1) {
            [newX, newY] = [initX + i, initY + j];
            [i, j] = [size, size];
          }
        }
      }

      ship.rows = this.ships[shipIndex].cols;
      ship.cols = this.ships[shipIndex].rows;
      ship.x = newX;
      ship.y = newY;
      ship.orientation = getNewOrientation(this.ships[shipIndex].orientation);

      let currentBoard = placeShips(this.rows, this.cols, tempShips);
      if (isPlacementPossible(currentBoard, ship, this.rows, this.cols)) {
        this.ships[shipIndex] = ship;
      }
    },
  },
};
</script>

<style lang="scss">
.placement-tips {
  font-size: 0.85rem;
  line-height: 1.4;
  opacity: 0.8;

  width: var(--board-size);

  & p {
    text-transform: uppercase;
    margin-top: 0;
    margin-bottom: var(--gap-xs);
  }

  & ul {
    margin: var(--gap-sm);
    margin-left: 0;
    list-style: decimal-leading-zero;
  }
}
</style>