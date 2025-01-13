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
          :disabled="isVerifying"
        />
        <button
          @click="authenticate"
          class="w-full bg-blue-600 hover:bg-blue-700 text-gray-100 font-bold py-3 px-8 rounded-lg transition-colors flex items-center justify-center gap-2"
          :disabled="isVerifying"
        >
          <font-awesome-icon 
            v-if="isVerifying" 
            icon="spinner" 
            class="animate-spin"
          />
          {{ isVerifying ? 'Verifying...' : 'Authenticate' }}
        </button>
        <div 
          v-if="error" 
          class="text-red-500 text-sm text-center"
        >
          {{ error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '../composables/useToast'

const router = useRouter()
const toast = useToast()
const token = ref('')
const isVerifying = ref(false)
const error = ref('')

const authenticate = async () => {
  if (!token.value.trim()) return
  
  error.value = ''
  isVerifying.value = true
  
  try {
    // Try to make a protected request to verify the token
    const response = await fetch('/api/save_poem', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token.value.trim()}`
      },
      body: JSON.stringify({ 
        id: 'test',
        content: 'test'
      })
    })
    
    if (response.ok) {
      // If the token works, save it and redirect
      localStorage.setItem('auth_token', token.value.trim())
      toast.success('Successfully authenticated')
      router.push('/')
    } else {
      error.value = 'Invalid token'
    }
  } catch (e) {
    error.value = 'Failed to verify token'
    console.error('Auth error:', e)
  } finally {
    isVerifying.value = false
  }
}
</script> 