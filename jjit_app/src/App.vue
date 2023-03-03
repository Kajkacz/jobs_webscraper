<template>
  <div class="menu-container">
    <div class="menu-header" @click="toggleMenu">
      <span>Menu</span>
      <!-- <v-icon>{{ menuOpen ? 'mdi-menu-open' : 'mdi-menu' }}</v-icon> -->
    </div>
    <div class="menu-body" :class="{ 'menu-body-open': menuOpen }" v-if="menuOpen">>
      <v-list style="display: flex; flex-direction: column;" >
        <v-list-item v-for="(item, index) in items" :key="index" @click="selectItem(item)">
          <v-list-item-title>{{ item }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </div>
  </div>
  <div class="menu-content">
    <div v-if="selectedItem === 'Earnings Plot'">
      <EarningsPlot />
    </div>
    <div v-else-if="selectedItem === 'Cities Plot'">
      <CitiesPlot />
    </div>
    <div v-else-if="selectedItem === 'General Info'">
      This webpage info, TODO
    </div>
  </div>
</template>

<script>
import EarningsPlot from './components/EarningsPlot.vue'
import CitiesPlot from './components/CitiesPlot.vue'

export default {
  name: 'App',
  components: {
    EarningsPlot,
    CitiesPlot
  },
  data() {
    return {
      items: ['Earnings Plot', 'Cities Plot', 'General Info'],
      selectedItem: 'Earnings Plot',
      menuOpen: false
    }
  },
  methods: {
    selectItem(item) {
      console.log(`Selected item: ${item}`)
      this.selectedItem = item
      this.toggleMenu();
    },
    toggleMenu() {
      this.menuOpen = !this.menuOpen;
    },
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

.menu-container {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 1000;
}

.menu-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100px;
  height: 36px;
  background-color: #1976d2;
  color: #ffffff;
  font-size: 16px;
  font-weight: 500;
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.menu-header:hover {
  background-color: #1565c0;
}

.menu-header v-icon {
  font-size: 20px;
}

.menu-body {
  position: absolute;
  top: 48px;
  right: 0;
  width: max-content;
  background-color: #a4a15c;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
  border-radius: 4px;
  overflow: hidden;
  transition: transform 0.2s ease;
  transform: translateY(-100%);
  display: flex;
  flex-direction: row;
}

.menu-body-open {
  transform: translateY(0%);
}
.menu-button {
  margin: 0;
}

.menu-list {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12), 0 0 2px rgba(0, 0, 0, 0.24);
}

.menu-content {
  margin-top: 24px;
}

.v-btn {
  text-transform: none;
  font-weight: 500;
  color: #ffffff;
}

.v-list-item__title {
  font-size: 16px;
}
</style>
