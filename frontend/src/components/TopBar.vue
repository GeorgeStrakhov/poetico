<template>
  <div class="flex justify-between items-center mb-8 top-bar">
    <button @click="$emit('toggle-sidebar')" class="top-bar-icon text-gray-300 hover:text-white">
      <font-awesome-icon icon="bars" class="text-xl" />
    </button>
    <div class="flex items-center space-x-6">
      <button 
        @click="$emit('generate-lines')" 
        class="top-bar-icon text-gray-300 hover:text-white flex items-center space-x-2"
      >
        <font-awesome-icon icon="magic" class="text-xl" />
        <span class="text-sm">⌘ + Enter</span>
      </button>
      <button 
        v-if="hasAlternatives" 
        @click="$emit('generate-more')" 
        class="top-bar-icon text-gray-300 hover:text-white"
      >
        <font-awesome-icon icon="sync" class="text-xl" />
      </button>
      <button 
        @click="$emit('toggle-fullscreen')" 
        class="top-bar-icon text-gray-300 hover:text-white flex items-center space-x-2"
      >
        <font-awesome-icon :icon="isFullscreen ? 'compress' : 'expand'" class="text-xl" />
        <span class="text-sm">⌘U</span>
      </button>
      <button 
        @click="$emit('save-poem')" 
        class="top-bar-icon text-gray-300 hover:text-white" 
        :class="{'text-yellow-500': hasUnsavedChanges}"
      >
        <font-awesome-icon icon="save" class="text-xl" />
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  isSidebarOpen: {
    type: Boolean,
    required: true
  },
  hasAlternatives: {
    type: Boolean,
    required: true
  },
  hasUnsavedChanges: {
    type: Boolean,
    required: true
  },
  isFullscreen: {
    type: Boolean,
    required: true
  }
})

defineEmits([
  'toggle-sidebar',
  'generate-lines',
  'generate-more',
  'toggle-fullscreen',
  'save-poem'
])
</script>
