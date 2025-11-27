<!--
  アプリケーションルートコンポーネント
  
  Vue Routerによるルーティングを行う。
-->
<template>
  <router-view />
</template>

<script setup>
/**
 * Appコンポーネント
 * 
 * アプリケーションのルートコンポーネント。
 * Vue Routerの<router-view>を表示する。
 */
</script>

<style>
/* グローバルスタイル */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: #f5f5f5;
  color: #333;
  line-height: 1.6;
}

a {
  color: inherit;
  text-decoration: none;
}

button {
  font-family: inherit;
}
</style>
