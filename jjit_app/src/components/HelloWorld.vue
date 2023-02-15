<template>
  <div>
    <Plotly :data="data" :layout="layout" :display-mode-bar="true"></Plotly>
    <ul v-for="(item, index) in items" :key="index">
      <li>{{ item.salary_average }}</li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios';
import { Plotly } from 'vue-plotly'

export default {
  components: {
    Plotly
  },    
  data() {
    return {
      items: [],
      data:[],
      layout:{
        title: "My graph"
      }
    }
  },
  mounted() {
    axios.get('http://localhost:8000/offers')
      .then((response) => {
          this.items = response.data.data
          this.data = {
                x: response.x,
                y: response.y,
                type:"bar"
          }
      });
  },
};
</script>
