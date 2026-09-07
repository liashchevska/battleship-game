import { createStore } from 'vuex'
import { zeros } from "../helpers";
import router from "@/router";
import axios from "axios";


const initialState = {
  gameId: null,
  ships: [],
  shipsPlaced: false,
  opponentType: 'computer',
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
  loading: false,
};

const mutate = (state, prop, value) => {
  state[prop] = value;
};

export default createStore({
  state: {
    ...initialState,
    connectionLost: false,
    
    socket: null,
    handler: null,

    rows: 10,
    cols: 10
  },

  getters: {
    friendAsOpponent: state => {
      return state.opponentType === "friend"
    },
    isWaitingForOpponent: state => {
      return !state.gameStarted && state.shipsPlaced
    },
    isGameActive: (state, getters) => {
      return !(getters.isWaitingForOpponent || state.isOver || state.opponentLeft)
    }
  },
  mutations: {
    setConnectionLost: (state, isLost) => {
      mutate(state, "connectionLost", isLost)
    },
    updateShips: (state, ships) => {
      mutate(state, "ships", ships);
    },
    setOpponent: (state, opponent) => {
      mutate(state, "opponentType", opponent);
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
    updateSocket: (state, socket) => {
      mutate(state, "socket", socket);
    },
    closeSocket: state => {
      state.socket.close();
    },
    reset: state => {
      Object.assign(state, initialState);
      state.socket = null;
      state.handler = null;
      state.connectionLost = false;
    },
    addListeners: (state, handler) => {
      state.handler = handler;
      state.socket.onmessage = handler;
    },
    setLoading(state, loading) {
      state.loading = loading;
    },
  },

  actions: {
    initSocket({ state, commit }, { handler, onOpen }) {
      const socket = new WebSocket(
        `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/`
      );
      socket.intentionalClose = false;

      socket.onmessage = handler;
      socket.onopen = () => {
        onOpen(socket);
      };

      socket.onclose = () => {
        console.log('Connection closed.')
        if (!socket.intentionalClose) {
          console.log("Connection lost.");
          commit("setConnectionLost", true);
        }
      };

      commit("updateSocket", socket);
    },


    startGame({ state, dispatch }, handler) {
      let payload = {
        action: "start",
        ships: state.ships,
        game_to_join_id: state.gameId,
        opponent_type: state.opponentType,
      };

      dispatch('initSocket', {
        handler, onOpen: socket => {
          socket.send(JSON.stringify(payload));
        }
      });
    },

    createGameWith({ commit }, opponent) {
      commit("setOpponent", opponent)
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

    initGame({ commit }, { gameId, opponent }) {
      commit("setGameId", gameId);
      commit("setOpponent", opponent);
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

    resetGame({ state, commit, dispatch }) {
      commit("reset");
      dispatch("randomizeShips");
      if (router.currentRoute.value.path != "/") {
        router.push({ name: "Game" });
      }
    },

    leaveGame({ state, dispatch }) {
      if (!state.socket) {
        return;
      }

      state.socket.intentionalClose = true;

      state.socket.send(JSON.stringify({
        action: "leave"
      }));

      state.socket.close();

      dispatch("resetGame");
    }

  }
});
