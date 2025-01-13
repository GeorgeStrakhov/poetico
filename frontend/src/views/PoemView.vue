<template>
  <div class="min-h-screen bg-dark p-8">
    <div class="max-w-2xl mx-auto">
      <div class="mb-8 flex justify-between items-center">
        <router-link to="/v" class="text-gray-400 hover:text-white">
          ← Back to list
        </router-link>
        <div class="text-sm text-gray-400" v-if="created">
          {{ formatDate(created) }}
        </div>
      </div>
      <div class="font-serif whitespace-pre-wrap leading-relaxed">{{ content }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const content = ref('')
const created = ref(null)

const formatDate = (isoDate) => {
  const date = new Date(isoDate)
  return date.getFullYear() + '-' + 
    String(date.getMonth() + 1).padStart(2, '0') + '-' +
    String(date.getDate()).padStart(2, '0') + ' ' +
    String(date.getHours()).padStart(2, '0') + ':' +
    String(date.getMinutes()).padStart(2, '0') + ':' + 
    String(date.getSeconds()).padStart(2, '0')
}

const loadPoem = async (id) => {
  try {
    const [poemResponse, poemsResponse] = await Promise.all([
      fetch(`/api/poem/${id}`),
      fetch('/api/list_poems')
    ])
    
    if (!poemResponse.ok) {
      router.push({ name: 'not-found' })
      return
    }
    
    const poemData = await poemResponse.json()
    const poemsList = await poemsResponse.json()
    
    content.value = poemData.content
    const poemInfo = poemsList.find(p => p.id === id)
    if (poemInfo) {
      created.value = poemInfo.created
    }
  } catch (error) {
    console.error('Error loading poem:', error)
    router.push({ name: 'not-found' })
  }
}

onMounted(() => {
  if (route.params.id) {
    loadPoem(route.params.id)
  }
})
</script> 