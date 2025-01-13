<template>
  <div 
    id="sidebar" 
    :class="['sidebar', {'closed': !isOpen}]" 
    class="fixed top-0 left-0 h-full w-64 bg-dark-lighter p-4 overflow-y-auto border-r border-gray-800 flex flex-col"
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
    <div class="space-y-2 flex-grow">
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
    
    <!-- Download Link -->
    <router-link 
      to="/download" 
      class="mt-4 p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded flex items-center gap-2 transition-colors"
    >
      <font-awesome-icon :icon="['fas', 'download']" />
      <span>Download</span>
    </router-link>
  </div>
</template>

<script setup>
import { useAuth } from '../composables/useAuth'
import { useRouter } from 'vue-router'
import { useToast } from '../composables/useToast'

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

const router = useRouter()
const toast = useToast()
const { getAuthHeaders } = useAuth()
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
      method: 'DELETE',
      headers: getAuthHeaders()
    })
    if (response.status === 401) {
      localStorage.removeItem('auth_token')
      router.push('/v')
      toast.error('Session expired. Please authenticate again.')
      return
    }
    if (response.ok) {
      emit('delete-poem', id)
    }
  } catch (error) {
    console.error('Error deleting poem:', error)
  }
}
</script>
