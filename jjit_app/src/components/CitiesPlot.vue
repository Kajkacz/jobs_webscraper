<template>
<div style="display: inline-block; margin-right: 20px;">
  Offers count:
  <div>Lower Threshold</div>
  <input v-model="min_count" type="text">
  <div>Upper Threshold</div>
  <input v-model="max_count" type="text">
</div>
<div style="display: inline-block;">
  Earnings:
  <div>Lower Threshold</div>
  <input v-model="min_cash" type="text">
  <div>Upper Threshold</div>
  <input v-model="max_cash" type="text">
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
      min_count: 600,
      max_count: 50000,
      min_cash: 0,
      max_cash: 100000,
    }
  },

  mounted() {
    this.getData();
  },

  watch: {
    min_count(newValue) {
      this.getData(this.max_count,newValue,this.min_cash,this.max_cash);
    },
    max_count(newValue) {
      this.getData(newValue,this.min_count,this.min_cash,this.max_cash);
    },
    min_cash(newValue) {
      this.getData(this.max_count,this.min_count,newValue,this.max_cash);
    },
    max_cash(newValue) {
      this.getData(this.max_count,this.min_count,this.min_cash,newValue);
    }
  },

  methods: {
    getData(upper_threshold_count = this.max_count, lower_threshold_count = this.min_count,lower_threshold_cash = this.min_cash, upper_threshold_cash = this.max_cash) {
      axios.get(`http://127.0.0.1:8000/offers?mode=cities&upper_threshold_count=${upper_threshold_count}&lower_threshold_count=${lower_threshold_count}&upper_threshold_cash=${upper_threshold_cash}&lower_threshold_cash=${lower_threshold_cash}`)
        .then(response => {
          const data = response.data;
          // Check that data.x and data.y contain the expected values
          console.log(data); 
          console.log(data.x, data.y); 

          const trace = {
            x: data.x,
            y: data.y,
            type: 'bar'
          };
          
          const layout = {
            xaxis: {
              tickvals: data.x.map((val, index) => index),
              ticktext: data.x,
              tickangle: -45,
              title: 'City',


            },
            yaxis: {
              range: [Math.min.apply(null, data.y)-4000, Math.max.apply(null, data.y) + 2000],
              title: 'Average earnings',
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
