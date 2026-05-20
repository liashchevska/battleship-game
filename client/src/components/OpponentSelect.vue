<template>
  <div class="opponent-select">
    <div :style="{ 'margin-bottom': '5px' }">opponent type:</div>
    <template v-if="gameId == null">
      <button :class="['btn', !friendAsOpponent ? 'btn-primary' : 'btn-secondary']" @click="createGameWithRandomOpponent">
        random
      </button>
      <button :class="['btn', friendAsOpponent ? 'btn-primary' : 'btn-secondary']" @click="createGameWithFriendOpponent">
        friend
      </button>
    </template>
    <template v-else>
      <button class="btn btn-primary friend-selected ">friend</button>
    </template>
  </div>
</template>

<script>
import { mapActions, mapState } from "vuex";
export default {
  computed: {
    ...mapState(["gameId", "friendAsOpponent"])
  },
  methods: {
    ...mapActions([
      "createGameWithFriendOpponent",
      "createGameWithRandomOpponent"
    ])
  }
};
</script>
