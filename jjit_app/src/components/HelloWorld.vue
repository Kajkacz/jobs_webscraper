<template>
  <div>
    <div>Lower Threshold</div>
    <input v-model="min" type="text">
    <div>Upper Threshold</div>
    <input v-model="max" type="text">
  </div>
  <div>
    <div id="my-chart"></div>
  </div>
</template>

<script>
import axios from 'axios';
import Plotly from 'plotly.js-dist';

export default {
  data() {
    return {
      items: [],
      data: {},
      min: 0,
      max: 100,
    }
  },

  mounted() {
    this.getData(0,1000);
  },

  watch: {
    value(newValue) {
      this.getData(newValue);
    }
  },

  methods: {
    getData(upper_threshold = this.max, lower_threshold = this.min) {
      axios.get(`http://localhost:8000/offers?upper_threshold=${upper_threshold}&lower_threshold=${lower_threshold}`)
        .then(response => {
          const data = response.data;

          // Check that data.x and data.y contain the expected values
          console.log(data.x, data.y);

          const trace = {
            x: data.x,
            y: data.y,
            type: 'bar'
          };
          
          const layout = {
            xaxis: {
              tickvals: data.x.map((val, index) => index),
              ticktext: data.x
            }
          };

          Plotly.newPlot('my-chart', [trace], layout);
        })
        .catch(error => {
          console.error(error);
        });
    }
  }
};
</script>
