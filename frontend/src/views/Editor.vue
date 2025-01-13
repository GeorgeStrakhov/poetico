<template>
  <div :class="{ 'fullscreen': isFullscreen }">
    <Sidebar 
      :is-open="isSidebarOpen"
      :poems="poems"
      @toggle="toggleSidebar"
      @load-poem="loadPoem"
      @delete-poem="handlePoemDelete"
    />

    <div class="flex min-h-screen">
      <main class="flex-1 p-8 fixed inset-0 overflow-auto">
        <div class="max-w-2xl mx-auto pb-32">
          <TopBar 
            :is-sidebar-open="isSidebarOpen"
            :has-alternatives="hasAlternatives"
            :has-unsaved-changes="hasUnsavedChanges"
            :is-fullscreen="isFullscreen"
            :is-generating="isGenerating"
            @toggle-sidebar="toggleSidebar"
            @generate-lines="generateLines"
            @generate-more="generateMore"
            @toggle-fullscreen="toggleFullscreen"
            @save-poem="savePoem"
          />

          <WritingArea 
            v-model="content"
            ref="textarea"
            @content-changed="contentChanged"
          />
        </div>
      </main>
    </div>

    <EditModal 
      v-if="editingLine !== null"
      v-model="editedLine"
      :ref="el => editTextarea = el"
      @close="closeEdit"
      @confirm="confirmEdit"
    />

    <SuggestionsModal 
      v-if="alternatives.length"
      :alternatives="alternatives"
      :editing-line="editingLine"
      :edited-line="editedLine"
      :context="getLastLine(content)"
      @select="selectLine"
      @edit="openEdit"
      @close="alternatives = []"
      @generate-more="generateMore"
      @confirm-edit="confirmEdit"
      @close-edit="closeEdit"
      @update:edited-line="editedLine = $event"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Sidebar from '../components/Sidebar.vue'
import TopBar from '../components/TopBar.vue'
import WritingArea from '../components/WritingArea.vue'
import EditModal from '../components/EditModal.vue'
import SuggestionsModal from '../components/SuggestionsModal.vue'
import { useToast } from '../composables/useToast'

// State
const content = ref('')
const currentPoemId = ref(null)
const alternatives = ref([])
const poems = ref([])
const isSidebarOpen = ref(false)
const hasUnsavedChanges = ref(false)
const lastSavedContent = ref('')
const editingLine = ref(null)
const editedLine = ref('')
const editTextarea = ref(null)
const textarea = ref(null)
const contentHeight = ref(0)
const isFullscreen = ref(false)
const isGenerating = ref(false)

const API_URL = '/api'

const route = useRoute()
const router = useRouter()
const toast = useToast()

// Computed
const hasAlternatives = computed(() => alternatives.value?.length > 0)
const isSuggestionsModalOpen = computed(() => alternatives.value?.length > 0)

// Methods
const generateId = (length = 10) => {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  return Array.from(crypto.getRandomValues(new Uint8Array(length)))
    .map(x => chars[x % chars.length])
    .join('')
}

const focusTextarea = () => {
  nextTick(() => {
    const textareaEl = textarea.value?.$el || textarea.value
    if (textareaEl) {
      textareaEl.focus()
    }
  })
}

const updateContentHeight = () => {
  nextTick(() => {
    const textareaEl = textarea.value?.$el || textarea.value
    if (textareaEl) {
      textareaEl.style.height = 'auto'
      textareaEl.style.height = textareaEl.scrollHeight + 'px'
    }
  })
}

const contentChanged = () => {
  hasUnsavedChanges.value = content.value !== lastSavedContent.value
  updateContentHeight()
}

const generateLines = async () => {
  try {
    editingLine.value = null
    isGenerating.value = true
    const response = await fetch(`${API_URL}/generate_line`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ current_text: content.value.trim() })
    })
    const data = await response.json()
    alternatives.value = data.alternatives
  } catch (error) {
    console.error('Generation error:', error)
  } finally {
    isGenerating.value = false
  }
}

const generateMore = generateLines

const selectLine = async (index, customText = null) => {
  const selectedText = customText || alternatives.value[index]
  const allAlternatives = [...alternatives.value]  // Create a copy for the backend
  
  try {
    await fetch(`${API_URL}/record_preference`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        current_text: content.value.trim(),
        alternatives: allAlternatives,
        chosen: selectedText
      })
    })
  } catch (error) {
    console.error('Error recording preference:', error)
  }
  
  const scrollTop = window.scrollY
  
  content.value = content.value.trim() + '\n' + selectedText
  alternatives.value = []
  hasUnsavedChanges.value = true
  editingLine.value = null
  
  nextTick(() => {
    const textareaEl = textarea.value?.$el?.querySelector('textarea') || textarea.value
    if (textareaEl) {
      textareaEl.focus()
      const newPosition = content.value.length
      textareaEl.setSelectionRange(newPosition, newPosition)
      
      window.scrollTo({
        top: scrollTop + 50,
        behavior: 'instant'
      })
    }
  })
}

const savePoem = async () => {
  if (!content.value.trim()) return

  try {
    const response = await fetch(`${API_URL}/save_poem`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        id: currentPoemId.value || generateId(),
        content: content.value 
      })
    })
    const data = await response.json()
    currentPoemId.value = data.id
    lastSavedContent.value = content.value
    hasUnsavedChanges.value = false
    await loadPoemsList()
    
    router.push(`/p/${currentPoemId.value}`)
    toast.success('Saved')
  } catch (error) {
    console.error('Save error:', error)
    toast.error('Failed to save...')
  }
}

const loadPoem = async (id) => {
  if (hasUnsavedChanges.value && !confirm('You have unsaved changes. Continue?')) {
    return
  }

  try {
    const response = await fetch(`${API_URL}/poem/${id}`)
    if (!response.ok) {
      if (response.status === 404) {
        content.value = ''
        currentPoemId.value = null
        lastSavedContent.value = ''
        hasUnsavedChanges.value = false
        alternatives.value = []
        editingLine.value = null
        router.push('/not-found')
        return
      }
      throw new Error('Failed to load poem')
    }
    const data = await response.json()
    content.value = data.content
    currentPoemId.value = id
    lastSavedContent.value = data.content
    hasUnsavedChanges.value = false
    isSidebarOpen.value = false
    alternatives.value = []
    editingLine.value = null
    router.push(`/p/${id}`)
    focusTextarea()
  } catch (error) {
    console.error('Load error:', error)
    toast.error('Failed to load poem')
  }
}

const loadPoemsList = async () => {
  try {
    const response = await fetch(`${API_URL}/list_poems`)
    poems.value = await response.json()
  } catch (error) {
    console.error('List error:', error)
  }
}

const closeEdit = () => {
  editingLine.value = null
  editedLine.value = ''
}

const openEdit = (index) => {
  editingLine.value = index
  editedLine.value = alternatives.value[index]
  nextTick(() => {
    const textareaEl = editTextarea.value?.$el?.querySelector('textarea') || editTextarea.value
    if (textareaEl) {
      textareaEl.focus()
      textareaEl.setSelectionRange(editedLine.value.length, editedLine.value.length)
    }
  })
}

const confirmEdit = () => {
  if (editingLine.value !== null && editedLine.value.trim()) {
    selectLine(editingLine.value, editedLine.value.trim())
    closeEdit()
  }
}

const getLastLine = (text) => {
  const lines = text.trim().split('\n')
  return lines[lines.length - 1] || ''
}

const toggleFullscreen = async () => {
  isFullscreen.value = !isFullscreen.value
  if (isFullscreen.value) {
    isSidebarOpen.value = false
    try {
      await document.documentElement.requestFullscreen()
    } catch (err) {
      console.log('Error attempting to enable fullscreen:', err)
    }
  } else {
    if (document.fullscreenElement) {
      try {
        await document.exitFullscreen()
      } catch (err) {
        console.log('Error attempting to exit fullscreen:', err)
      }
    }
  }
}

const toggleSidebar = () => isSidebarOpen.value = !isSidebarOpen.value

const handleKeyboard = (e) => {
  if (e.key === 'Escape') {
    alternatives.value = []
    editingLine.value = null
    isSidebarOpen.value = false
    return
  }

  if (e.metaKey || e.ctrlKey) {
    switch (e.key.toLowerCase()) {
      case 'p':
        e.preventDefault()
        if (hasUnsavedChanges.value && !confirm('You have unsaved changes. Continue?')) {
          return
        }
        content.value = ''
        currentPoemId.value = null
        lastSavedContent.value = ''
        hasUnsavedChanges.value = false
        alternatives.value = []
        editingLine.value = null
        router.push('/')
        focusTextarea()
        break
      case 'enter':
        if (!isSuggestionsModalOpen.value) {
          e.preventDefault()
          generateLines()
        }
        break
      case 'l':
        e.preventDefault()
        toggleSidebar()
        break
      case 's':
        e.preventDefault()
        savePoem()
        break
      case 'u':
        e.preventDefault()
        toggleFullscreen()
        break
    }
  }
}

const handlePoemDelete = async (id) => {
  if (id === currentPoemId.value) {
    content.value = ''
    currentPoemId.value = null
    lastSavedContent.value = ''
    hasUnsavedChanges.value = false
    router.push('/')
  }
  
  await loadPoemsList()
  toast.success('Deleted successfully')
}

// Watchers
watch(() => content.value, () => {
  nextTick(() => {
    updateContentHeight()
  })
})

watch(() => route.params.id, (newId) => {
  if (newId && newId !== currentPoemId.value) {
    loadPoem(newId)
  }
}, { immediate: true })

// Lifecycle
onMounted(async () => {
  document.addEventListener('keydown', handleKeyboard)
  await loadPoemsList()
  
  nextTick(() => {
    updateContentHeight()
    const poemId = route.params.id
    if (poemId) {
      loadPoem(poemId).then(() => focusTextarea())
    } else {
      focusTextarea()
    }
  })
  
  window.addEventListener('resize', updateContentHeight)
  
  document.addEventListener('fullscreenchange', () => {
    if (!document.fullscreenElement) {
      isFullscreen.value = false
    }
  })
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeyboard)
  window.removeEventListener('resize', updateContentHeight)
  document.removeEventListener('fullscreenchange', () => {})
})

// Navigation warning
window.onbeforeunload = () => {
  if (hasUnsavedChanges.value) {
    return 'You have unsaved changes. Continue?'
  }
}
</script> 