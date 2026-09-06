<template>
    <div class="status-indicator text-label">
        <span v-if="props.displayDot" class="dot"></span>
        <span>{{ props.text }}</span>
    </div>
</template>

<script setup>
const props = defineProps({
    text: String,
    displayDot: Boolean
})
</script>

<style lang="scss" scoped>
@use '@/assets/scss/mixins';
@use 'sass:color';

.status-indicator {
    display: inline-flex;
    align-items: center;
    gap: var(--gap-sm);
}

.dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    animation: flicker 1.5s infinite ease-in-out;
}

$variants: "you", "opponent", "won", "lost", "left", "wait";

@each $variant in $variants {
    .#{$variant} .dot {
        @include mixins.themify using ($theme-map) {
            $color: mixins.theme-based($theme-map, $variant);
            background-color: $color;

            @if $variant =='won' {
                box-shadow: 0 0 10px color.scale($color, $alpha: 60%);
            }
        }
    }
}

.won.dot {
    box-shadow: 0 0 10px rgba(46, 230, 198, 0.6);
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