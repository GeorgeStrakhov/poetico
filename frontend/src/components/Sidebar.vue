<template>
  <div 
    id="sidebar" 
    :class="['sidebar', {'closed': !isOpen}]" 
    class="fixed top-0 left-0 h-full w-64 bg-dark-lighter p-4 overflow-y-auto border-r border-gray-800"
  >
    <div class="flex justify-between items-center mb-4">
      <button @click="$emit('toggle')" class="text-gray-400 hover:text-white">
        <font-awesome-icon icon="times" />
      </button>
      <a href="/" class="text-gray-400 hover:text-white flex items-center">
        <font-awesome-icon icon="plus" />
        <span class="ml-2">New</span>
        <span class="ml-2 text-xs opacity-50">⌘P</span>
      </a>
    </div>
    <div class="space-y-2">
      <div 
        v-for="poem in poems" 
        :key="poem.id" 
        class="poem-item p-2 hover:bg-gray-800 rounded group"
      >
        <div class="flex justify-between items-center gap-2">
          <div 
            class="flex-grow cursor-pointer min-w-0"
            @click="$emit('load-poem', poem.id)"
          >
            <div class="text-sm text-gray-400">{{ formatDate(poem.created) }}</div>
            <div class="truncate">{{ poem.first_line }}</div>
          </div>
          <button 
            @click="deletePoem(poem.id)"
            class="text-gray-500 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
            title="Delete poem"
          >
            <font-awesome-icon icon="trash" class="text-sm" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  poems: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['toggle', 'load-poem', 'delete-poem'])

const formatDate = (isoDate) => {
  return new Date(isoDate).toLocaleDateString()
}

const deletePoem = async (id) => {
  if (!confirm('Are you sure you want to delete this poem?')) {
    return
  }
  
  try {
    const response = await fetch(`/api/poem/${id}`, {
      method: 'DELETE'
    })
    if (response.ok) {
      emit('delete-poem', id)
    }
  } catch (error) {
    console.error('Error deleting poem:', error)
  }
}
</script>
