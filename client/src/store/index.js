import { createStore } from 'vuex'
import { zeros } from "../helpers";
import router from "@/router";
import axios from "axios";


const initialState = {
  gameId: null,
  ships: [],
  shipsPlaced: false,
  friendAsOpponent: false,
  gameStarted: false,
  isOver: false,
  youWon: false,
  opponentLeft: false,
  yourTurn: false,
  board: [],
  shots: [],
  opponent: [],
  opponentShips: [],
  gameIsInvalid: false,
  loading: false
};

const mutate = (state, prop, value) => {
  state[prop] = value;
};

export default createStore({
  state: {
    ...initialState,

    socket: new WebSocket(
      `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/`
    ),

    handler: null,

    rows: 10,
    cols: 10
  },

  getters: {
    isWaitingForOpponent: state => {
      return !state.gameStarted && state.shipsPlaced
    },
    isGameActive: (state, getters) => {
      return !(getters.isWaitingForOpponent || state.isOver || state.opponentLeft)
    }
  },
  mutations: {
    updateShips: (state, ships) => {
      mutate(state, "ships", ships);
    },
    setOpponent: (state, friend) => {
      mutate(state, "friendAsOpponent", friend);
    },
    startGame: state => {
      mutate(state, "gameStarted", true);
    },
    placeShips: state => {
      mutate(state, "shipsPlaced", true);
    },
    setGameId: (state, id) => {
      mutate(state, "gameId", id);
    },
    opponentLeft: state => {
      mutate(state, "opponentLeft", true);
    },
    gameIsInvalid: state => {
      mutate(state, "gameIsInvalid", true);
    },
    updateBoard: (state, board) => {
      mutate(state, "board", JSON.parse(board));
    },
    updateShots: (state, shots) => {
      mutate(state, "shots", JSON.parse(shots));
    },
    updateOpponent: (state, opponent) => {
      mutate(state, "opponent", JSON.parse(opponent));
    },
    updateOpponentShip: (state, opponentShips) => {
      mutate(state, "opponentShips", opponentShips);
    },
    updateCurrentTurn: (state, yourTurn) => {
      mutate(state, "yourTurn", yourTurn);
    },
    updateGameStatus: (state, isOver) => {
      mutate(state, "isOver", isOver);
    },
    updateGameWinner: (state, youWon) => {
      mutate(state, "youWon", youWon);
    },
    updateSocket: (state, url) => {
      mutate(state, "socket", new WebSocket(url));
    },
    closeSocket: state => {
      state.socket.close();
    },
    reset: state => {
      Object.assign(state, initialState);
    },
    addListeners: (state, handler) => {
      state.handler = handler;
      state.socket.onmessage = handler;
    },
    setLoading(state, loading) {
      state.loading = loading;
    }
  },

  actions: {
    initSocket({ commit, dispatch }, payload) {
      commit("addListeners", payload.handler);
      dispatch("randomizeShips");
      let gameId = router.currentRoute.value.params.id;
      gameId = gameId == undefined ? null : gameId;
      let friend = gameId == null ? false : true;
      commit("setOpponent", friend);
      commit("setGameId", gameId);
    },

    async createGameWithFriendOpponent({ commit, state }) {
      if (!state.friendAsOpponent) {
        commit("setOpponent", true);
      }
    },

    createGameWithRandomOpponent({ state, commit }) {
      if (state.friendAsOpponent) {
        commit("setOpponent", false);
      }
    },

    sendSocketMessage({ state }, payload) {
      state.socket.send(JSON.stringify(payload));
    },

    async randomizeShips({ state, commit }) {
      commit("setLoading", true);
      const response = await axios.get(`/random-board/?rows=${state.rows}&cols=${state.cols}`);
      commit("updateShips", response.data);
      commit("setLoading", false);
    },

    startGame({ state, dispatch }) {
      let payload = {
        action: "start",
        ships: state.ships,
        game_to_join_id: state.gameId,
        opponent_type:  state.friendAsOpponent ? "friend": "random",
      };
      dispatch("sendSocketMessage", payload);
    },

    updateGame({ commit }, data) {
      commit("updateBoard", data.you.board);
      commit("updateShots", data.you.shots);
      commit("updateOpponent", data.opponent.shots);
      commit("updateCurrentTurn", data.your_turn);
      commit("updateGameStatus", data.is_over);
      commit("updateGameWinner", data.you_won);
      commit("updateOpponentShip", data.opponent.shot_ships);
    },

    onSocketMessage({ commit, dispatch, state }, data) {
      if (data.action === "game.wait") {
        commit("setGameId", data.game_id);
        commit("placeShips");
        commit("updateBoard", data.you.board);
        commit("updateShots", data.you.shots);
        commit(
          "updateOpponent",
          JSON.stringify(zeros(state.rows, state.cols, 0))
        );
      } else if (data.action === "game.start") {
        commit("placeShips");
        commit("startGame");
        dispatch("updateGame", data.game);
      } else if (data.action === "game.update") {
        dispatch("updateGame", data.game);
      } else if (data.action == "game.leave") {
        commit("opponentLeft");
      } else if (data.type == "game.invalid") {
        commit("gameIsInvalid");
      }
    },

    makeMove({ dispatch }, payload) {
      payload = {
        action: "shoot",
        x: payload.x,
        y: payload.y
      };
      dispatch("sendSocketMessage", payload);
    },

    resetGame({ commit, dispatch }) {
      commit("reset");
      dispatch("randomizeShips");
      if (router.currentRoute.value.path != "/") {
        router.push({ name: "Game" });
      }
    },

    leaveGame({ dispatch }) {
      let payload = {
        action: "leave"
      };
      dispatch("sendSocketMessage", payload);
      dispatch("resetGame");
    }
  }
});
