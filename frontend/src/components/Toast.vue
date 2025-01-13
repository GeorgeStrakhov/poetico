<template>
  <Transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="transform -translate-y-2 opacity-0"
    enter-to-class="transform translate-y-0 opacity-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="transform translate-y-0 opacity-100"
    leave-to-class="transform -translate-y-2 opacity-0"
  >
    <div 
      v-if="show"
      class="fixed top-4 right-4 px-4 py-2 rounded-lg shadow-lg text-white z-50 font-normal bg-opacity-30"
      :class="typeClasses[type]"
    >
      <div class="flex items-center gap-2">
        <font-awesome-icon :icon="typeIcons[type]" class="text-sm" />
        <span>{{ message }}</span>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { FontAwesomeIcon } from '../fontawesome'

const props = defineProps({
  message: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'success',
    validator: (value) => ['success', 'error', 'info'].includes(value)
  },
  duration: {
    type: Number,
    default: 3000
  }
})

const show = ref(false)
let timeout = null

const typeClasses = {
  success: 'bg-green-600',
  error: 'bg-red-600',
  info: 'bg-blue-600'
}

const typeIcons = {
  success: 'check-circle',
  error: 'exclamation-circle',
  info: 'info-circle'
}

onMounted(() => {
  show.value = true
  timeout = setTimeout(() => {
    show.value = false
  }, props.duration)
})

onBeforeUnmount(() => {
  if (timeout) clearTimeout(timeout)
})
</script> 