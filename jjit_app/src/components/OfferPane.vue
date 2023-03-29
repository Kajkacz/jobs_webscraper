<template>
  <div>
    <h2>{{ offer.title }}</h2>
    <h4>{{ offer.position }}</h4>
    <p>{{ offer.description }}</p>
    <p>{{ offer.raw_salary }}</p>
    <p>{{ offer.address }}, {{ offer.city }}</p>
    <a :href="offer.link">See offer</a>
  </div>
</template>

<script>

export default {
  name: 'OfferPane',
  props: {
    offer: {
      type: Object,
      required: true,
    },
  },
};
</script>
<style scoped>
h2 {
  margin-bottom: 0;
}
h4 {
  margin-top: 0;
  font-weight: normal;
}
p {
  margin-bottom: 10px;
}
a {
  text-decoration: none;
  color: #0077c2;
}
a:hover {
  text-decoration: underline;
}
</style>


///
