<template>
  <div>
    <Plotly :data="data" :layout="layout" :display-mode-bar="false"></Plotly>
    <ul v-for="item in items" :key="item.title">
      <li>{{ item.title }}</li>
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
  data () {
    return {
      data:[{
        x: [1,2,3,4],
        y: [10,15,13,17],
        type:"scatter"
      }],
      layout:{
        title: "My graph"
      }
    }
  },
  mounted() {
    axios.get('http://localhost:8000/offers')
      .then((response) => {
          this.data = 
          {
              data:[{
                x: response.data,
                y: response.data,
                type:"scatter"
              }]
          }
      });
  },
};
</script>
