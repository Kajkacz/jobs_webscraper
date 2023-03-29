<template>
  <div>
    <offers :offers="offers"></offers>
  </div>
</template>
<script>
import Offers from './Offers.vue';
import axios from 'axios';

export default {
  name: 'RandomOffers',
  components: {
    Offers,
  },
  data() {
    return {
      offers: [],
    };
  },
  mounted() {
    this.getData();
  },
  methods: {
    getData() {
      axios.get(`http://localhost:8000/offers?mode=rand&conut=10`)
        .then(response => {
          const data = response.data;
          // Check that data.x and data.y contain the expected values
          console.log(data); 
          this.offers = data.offers_list
        })
        .catch(error => {
          console.error(error);
        });
    }
  }
};
</script>