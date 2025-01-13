<template>
  <div class="min-h-screen bg-dark p-8">
    <div class="max-w-2xl mx-auto">
      <div class="space-y-4">
        <div 
          v-for="poem in poems" 
          :key="poem.id" 
          class="p-4 bg-dark-lighter rounded-lg hover:bg-gray-800 transition-colors"
        >
          <router-link :to="`/v/${poem.id}`" class="block">
            <div class="text-sm text-gray-400 mb-1">{{ formatDate(poem.created) }}</div>
            <div class="font-serif">{{ poem.first_line }}</div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const poems = ref([])

const formatDate = (isoDate) => {
  const date = new Date(isoDate)
  return date.getFullYear() + '-' + 
    String(date.getMonth() + 1).padStart(2, '0') + '-' +
    String(date.getDate()).padStart(2, '0') + ' ' +
    String(date.getHours()).padStart(2, '0') + ':' +
    String(date.getMinutes()).padStart(2, '0') + ':' + 
    String(date.getSeconds()).padStart(2, '0')
}

const loadPoems = async () => {
  try {
    const response = await fetch('/api/list_poems')
    poems.value = await response.json()
  } catch (error) {
    console.error('Error loading poems:', error)
  }
}

onMounted(() => {
  loadPoems()
})
</script> 