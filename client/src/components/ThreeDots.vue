<template>
    <span class="dot" v-for="i in 3" :key="i">.</span>
</template>

<style scoped lang="scss">
.dot {
    opacity: 0;
    animation: blink 1.4s infinite;
}

.dot:nth-child(2) {
    animation-delay: 0.2s;
}

.dot:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes blink {
    0%,
    20%  { opacity: 0; }
    50%  { opacity: 1; }
    100% { opacity: 0; }
}
</style>