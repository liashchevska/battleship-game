<template>
    <div class="status-indicator text-label">
        <span v-if="props.isActive" class="dot"></span>
        <span class="text-state">{{ props.text }}</span>
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
@use '@/assets/scss/mixins';

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
    animation: flicker 1.5s infinite ease-in-out;
}

$variants: "you", "opponent";

@each $variant in $variants {
    .#{$variant} .dot {
        @include mixins.themify using ($theme-map) {
            background-color: mixins.theme-based($theme-map, $variant);
        }
    }
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