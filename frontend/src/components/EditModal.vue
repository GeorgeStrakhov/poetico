<template>
  <div class="modal-backdrop" @click="$emit('close')">
    <div class="edit-modal" @click.stop>
      <div class="mb-4 text-xl">Edit line:</div>
      <textarea 
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        class="w-full bg-dark text-gray-200 p-2 rounded-lg border border-gray-700 mb-4"
        rows="3"
        @keydown.enter.prevent="$emit('confirm')"
        @keydown.esc="$emit('close')"
      ></textarea>
      <div class="flex justify-end gap-2">
        <button 
          class="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded"
          @click="$emit('close')"
        >Cancel</button>
        <button 
          class="px-3 py-1 bg-blue-600 hover:bg-blue-500 rounded"
          @click="$emit('confirm')"
        >Save</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    required: true
  }
})

defineEmits(['update:modelValue', 'close', 'confirm'])
</script>
