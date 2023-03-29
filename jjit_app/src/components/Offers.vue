<template>
  <div>
    <offer-pane v-for="(offer, index) in offers" :key="index" :offer="offer"></offer-pane>
  </div>
</template>
<script>
import OfferPane from './OfferPane.vue';

export default {
  name: 'OfferList',
  components: {
    OfferPane,
  },
  props: {
    offers: {
      type: Array,
      required: true,
    },
  },
};
</script>