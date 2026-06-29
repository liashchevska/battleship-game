import { createRouter, createWebHistory } from "vue-router"
import GameView from '@/views/GameView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "Game",
      component: GameView
    },
    {
      path: "/join:id?",
      name: "joinGame",
      component: GameView
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: "/"
    }
  ]
})

export default router