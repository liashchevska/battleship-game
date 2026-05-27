<template>
    <div class="status-indicator text-label">
        <span v-if="props.isActive" class="dot"></span>
        <span>{{ props.text }}</span>
    </div>
</template>

<script setup>
const props = defineProps({
    text: String,
    isActive: Boolean
})
</script>

<style lang="scss" scoped>
@use '@/assets/scss/variables';

.status-indicator {
    display: inline-flex;
    align-items: center;
    gap: variables.$gap-sm;
}

.dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #29d3c2;
    animation: flicker 1.5s infinite ease-in-out;
}

@keyframes flicker {
    0% {
        opacity: 0.4;
    }

    50% {
        opacity: 1;
    }

    100% {
        opacity: 0.4;
    }
}
</style>