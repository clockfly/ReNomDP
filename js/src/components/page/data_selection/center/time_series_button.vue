<template>
  <div id='time_series_button' @click='toggle_time_series'>
    <i class="fa fa-plus-square-o" v-if="!$store.state.show_time_series"></i>
    <i class="fa fa-minus-square-o" v-if="$store.state.show_time_series"></i>
    Time Series
  </div>
</template>

<script>
export default {
  name: 'TimeSeriesButton',
  methods: {
    toggle_time_series: function() {
      this.$store.commit('toggle_time_series');
    },
  }
}
</script>

<style lang='scss' scoped>
#time_series_button {
  font-size: 12px;
  line-height: 26px;
}
</style>