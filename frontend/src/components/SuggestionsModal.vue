<template>
  <div class="modal-backdrop" @click="$emit('close')">
    <div class="suggestions-modal" @click.stop>
      <div class="context-line">
        {{ context }}
      </div>
      <div class="suggestions-list">
        <div v-for="(line, index) in alternatives" 
             :key="index"
             class="suggestion-item group"
             :class="[`suggestion-${index + 1}`, {'editing': editingLine === index}]">
          <template v-if="editingLine === index">
            <textarea 
              :value="editedLine"
              @input="$emit('update:edited-line', $event.target.value)"
              class="w-full bg-dark text-gray-200 p-2 rounded-lg border border-gray-700"
              rows="2"
              @keydown.enter.prevent="$emit('confirm-edit')"
              @keydown.esc="$emit('close-edit')"
            ></textarea>
            <div class="flex gap-2">
              <button 
                class="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-200"
                @click="$emit('close-edit')"
              >
                Cancel
              </button>
              <button 
                class="px-3 py-1 bg-blue-600 hover:bg-blue-500 rounded text-sm text-gray-200"
                @click="$emit('confirm-edit')"
              >
                Save
              </button>
            </div>
          </template>
          <template v-else>
            <div class="flex items-center gap-3 w-full">
              <span class="suggestion-text flex-grow" @click="$emit('select', index)">
                {{ line }}
              </span>
              <button 
                class="px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                @click.stop="$emit('edit', index)"
              >
                edit
              </button>
            </div>
          </template>
        </div>
      </div>
      <div class="flex justify-between p-4 border-t border-gray-800">
        <button 
          class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded"
          @click="$emit('close')"
        >
          Cancel
        </button>
        <button 
          class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded"
          @click="$emit('generate-more')"
        >
          More
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  alternatives: {
    type: Array,
    required: true
  },
  editingLine: {
    type: Number,
    default: null
  },
  editedLine: {
    type: String,
    default: ''
  },
  context: {
    type: String,
    required: true
  }
})

defineEmits([
  'close',
  'select',
  'edit',
  'generate-more',
  'update:edited-line',
  'confirm-edit',
  'close-edit'
])
</script>
