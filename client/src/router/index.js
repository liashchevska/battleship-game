import { createRouter, createWebHistory } from "vue-router"
import Game from '@/views/Game.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "Game",
      component: Game
    },
    {
      path: "/join:id?",
      name: "joinGame",
      component: Game
    }
  ]
})

export default router