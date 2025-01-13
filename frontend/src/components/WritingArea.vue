<template>
  <div class="relative">
    <textarea 
      :value="modelValue"
      @input="handleInput"
      class="writing-area w-full text-xl leading-relaxed text-gray-100"
      placeholder="Start writing..."
    ></textarea>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'content-changed'])

const handleInput = (event) => {
  const value = event.target.value
  emit('update:modelValue', value)
  emit('content-changed')
}
</script>
