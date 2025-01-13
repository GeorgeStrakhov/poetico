import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'
import { FontAwesomeIcon } from './fontawesome'

const app = createApp(App)

app.component('font-awesome-icon', FontAwesomeIcon)
app.use(router)
app.mount('#app')
