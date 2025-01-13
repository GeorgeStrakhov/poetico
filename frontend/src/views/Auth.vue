<template>
  <div class="flex flex-col items-center justify-center min-h-screen p-4">
    <div class="bg-dark-lighter rounded-lg shadow-xl p-8 border border-gray-800 max-w-md w-full">
      <h1 class="text-2xl font-bold text-center mb-6 text-gray-100">Authentication</h1>
      <div class="space-y-4">
        <input 
          type="password"
          v-model="token"
          placeholder="Enter token"
          class="w-full bg-dark text-gray-200 p-3 rounded-lg border border-gray-700"
          @keyup.enter="authenticate"
        />
        <button
          @click="authenticate"
          class="w-full bg-blue-600 hover:bg-blue-700 text-gray-100 font-bold py-3 px-8 rounded-lg transition-colors"
        >
          Authenticate
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const token = ref('')

const authenticate = () => {
  if (!token.value.trim()) return
  
  localStorage.setItem('auth_token', token.value.trim())
  router.push('/')
}
</script> 