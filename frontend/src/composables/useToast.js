import { ref, h, render } from 'vue'
import Toast from '../components/Toast.vue'

const toasts = ref([])
let toastId = 0

export function useToast() {
  const show = (message, type = 'success', duration = 3000) => {
    const id = toastId++
    const container = document.createElement('div')
    
    const vnode = h(Toast, {
      message,
      type,
      duration,
      onVnodeBeforeUnmount: () => {
        // Remove from DOM after animation
        setTimeout(() => {
          render(null, container)
          document.body.removeChild(container)
          toasts.value = toasts.value.filter(t => t.id !== id)
        }, 200)
      }
    })
    
    document.body.appendChild(container)
    render(vnode, container)
    
    toasts.value.push({ id, container })
  }
  
  const success = (message, duration) => show(message, 'success', duration)
  const error = (message, duration) => show(message, 'error', duration)
  const info = (message, duration) => show(message, 'info', duration)
  
  return {
    show,
    success,
    error,
    info
  }
} 