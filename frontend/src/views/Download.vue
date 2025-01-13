<template>
  <div class="flex flex-col items-center min-h-screen p-4">
    <!-- Home Button -->
    <div class="w-full max-w-4xl mb-8 mt-8">
      <router-link 
        to="/" 
        class="inline-flex items-center gap-2 text-gray-400 hover:text-gray-100 transition-colors duration-200"
      >
        <font-awesome-icon :icon="['fas', 'arrow-left']" />
        <span>Back home</span>
      </router-link>
    </div>

    <div class="grid md:grid-cols-2 gap-6 max-w-4xl w-full">
      <!-- Poems Download Card -->
      <div class="bg-dark-lighter rounded-lg shadow-xl p-8 border border-gray-800">
        <h1 class="text-2xl font-bold text-center mb-6 text-gray-100">Download Texts</h1>
        <p class="text-gray-400 mb-8 text-center leading-relaxed">
          Download all texts in their current form<br />in a single zip file.
        </p>
        <div class="flex justify-center">
          <button
            @click="downloadPoems"
            class="bg-blue-600 hover:bg-blue-700 text-gray-100 font-bold py-3 px-8 rounded-lg flex items-center gap-3 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="isPoemsDownloading"
          >
            <font-awesome-icon 
              :icon="['fas', 'download']" 
              :class="{'animate-spin': isPoemsDownloading}"
            />
            <span>{{ isPoemsDownloading ? 'Preparing...' : 'Download Poems' }}</span>
          </button>
        </div>
      </div>

      <!-- Preferences Download Card -->
      <div class="bg-dark-lighter rounded-lg shadow-xl p-8 border border-gray-800">
        <h1 class="text-2xl font-bold text-center mb-6 text-gray-100">Download Taste Data</h1>
        <p class="text-gray-400 mb-8 text-center leading-relaxed">
          Download line preferences generated while<br />writing in JSONL format.
        </p>
        <div class="flex justify-center">
          <button
            @click="downloadPreferences"
            class="bg-purple-600 hover:bg-purple-700 text-gray-100 font-bold py-3 px-8 rounded-lg flex items-center gap-3 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="isPrefsDownloading"
          >
            <font-awesome-icon 
              :icon="['fas', 'database']" 
              :class="{'animate-spin': isPrefsDownloading}"
            />
            <span>{{ isPrefsDownloading ? 'Preparing...' : 'Download Data' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const isPoemsDownloading = ref(false)
const isPrefsDownloading = ref(false)

const downloadPoems = async () => {
  try {
    isPoemsDownloading.value = true
    const response = await fetch('/api/download_poems_zip')
    if (!response.ok) throw new Error('Download failed')
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'gspoems.zip'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (error) {
    console.error('Error downloading poems:', error)
    alert('Failed to download poems. Please try again.')
  } finally {
    isPoemsDownloading.value = false
  }
}

const downloadPreferences = async () => {
  try {
    isPrefsDownloading.value = true
    const response = await fetch('/api/download_preferences')
    if (!response.ok) throw new Error('Download failed')
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'line_preferences.jsonl'
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (error) {
    console.error('Error downloading preferences:', error)
    alert('Failed to download preferences. Please try again.')
  } finally {
    isPrefsDownloading.value = false
  }
}
</script> 