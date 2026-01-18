<template>
  <el-container class="app-container">
    <el-header>
      <div class="header-content">
        <div class="logo">
          <el-icon :size="24"><OfficeBuilding /></el-icon>
          <span>Real Estate System</span>
        </div>
        <el-menu
          :default-active="activeIndex"
          mode="horizontal"
          router
          class="header-menu"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>Home</span>
          </el-menu-item>
          <el-menu-item index="/properties">
            <el-icon><OfficeBuilding /></el-icon>
            <span>Properties</span>
          </el-menu-item>
          <el-menu-item index="/deals">
            <el-icon><Document /></el-icon>
            <span>Deals</span>
          </el-menu-item>
        </el-menu>
      </div>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
    <el-footer>
      <span>Real Property Deal Management System - CST8276 Project</span>
    </el-footer>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { HomeFilled, OfficeBuilding, Document } from '@element-plus/icons-vue'

const route = useRoute()
const activeIndex = computed(() => route.path)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', Arial, sans-serif;
}

.app-container {
  min-height: 100vh;
}

.el-header {
  background-color: #409eff;
  color: white;
  padding: 0 20px;
}

.header-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
  margin-right: 40px;
}

.header-menu {
  background-color: transparent;
  border-bottom: none;
  flex: 1;
}

.header-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.8);
}

.header-menu .el-menu-item:hover,
.header-menu .el-menu-item.is-active {
  color: white;
  background-color: rgba(255, 255, 255, 0.1);
}

.el-main {
  background-color: #f5f7fa;
  min-height: calc(100vh - 120px);
}

.el-footer {
  background-color: #545c64;
  color: white;
  text-align: center;
  line-height: 60px;
}
</style>
