/**
 * アプリケーションエントリーポイント
 * 
 * Vue.jsアプリケーションの初期化とプラグインの設定を行う。
 */

import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Vueアプリケーションの作成
const app = createApp(App)

// Piniaストアのセットアップ
app.use(createPinia())

// Vue Routerのセットアップ
app.use(router)

// アプリケーションのマウント
app.mount('#app')
