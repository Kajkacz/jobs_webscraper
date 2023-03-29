<template>
  
  <div>
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
    
    <h2>Filtered Offers by Technology</h2>
    <div class="technology-list">
      <div v-for="tech in technologies" :key="tech">
        <label>
          <input type="checkbox" v-model="selectedTechnologies" :value="tech">
          {{ tech }}
        </label>
      </div>
    </div>
    <h2>Filtered Data</h2>
    <ul>
      <li v-for="item in filteredData" :key="item.id">{{ item.name }}</li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      items: [],
      min_count: 600,
      max_count: 50000,
      min_cash: 0,
      max_cash: 100000,
      technologies: [],
      selectedTechnologies: [],
      offers: [ // TODO Add listener to get this dynamically
        { id: 1, name: 'Item 1', technologies: ['JavaScript', 'HTML'] },
        { id: 2, name: 'Item 2', technologies: ['CSS', 'React'] },
        { id: 3, name: 'Item 3', technologies: ['Vue', 'HTML'] },
        { id: 4, name: 'Item 4', technologies: ['JavaScript', 'Vue'] },
        { id: 5, name: 'Item 5', technologies: ['React', 'CSS'] },
      ]
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
    },
    selectedTechnologies(newValue) {
      this.getOffers(newValue);
    },
  },
  computed: {
    filteredData() {
      if (this.selectedTechnologies.length === 0) {
        return this.offers;
      } else {
        return this.offers.filter(item => {
          return this.selectedTechnologies.every(tech => item.technologies.includes(tech));
        });
      }
    }
  },

methods: {
  getOffers(technologies = this.selectedTechnologies) {
    axios.get(`http://localhost:8000/offers?mode=offers_by_tech&technologies=${technologies.join(',')}`)
    .then(response => {
        const offers = response.data.offers_list;
        console.log(offers); 
    }).catch(error => {
        console.error(error);
      })
  },
  getData(upper_threshold_count = this.max_count, lower_threshold_count = this.min_count,lower_threshold_cash = this.min_cash, upper_threshold_cash = this.max_cash) {
    axios.get(`http://localhost:8000/offers?mode=tech&upper_threshold_count=${upper_threshold_count}&lower_threshold_count=${lower_threshold_count}&upper_threshold_cash=${upper_threshold_cash}&lower_threshold_cash=${lower_threshold_cash}`)
      .then(response => {
        const data = response.data;
        console.log(data); 

        this.technologies = response.data.techs.sort((a, b) => a.localeCompare(b));
      })
      .catch(error => {
        console.error(error);
      });
  }
},
  created() {
    this.getData();
  }
}
</script>

<style>
.technology-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
</style>
