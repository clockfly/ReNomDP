<template>
  <div id='select_all_button' @click="set_select_all">
    <i class="fa fa-square" aria-hidden="true" v-if='selected_all'></i>
    <i class="fa fa-square-o" aria-hidden="true" v-if='!selected_all'></i>
    <input type='checkbox' id='select_all' @change='set_select_all'>
    <label for='select_all'>Select All</label>
  </div>
</template>

<script>
export default {
  name: 'TimeSeriesButton',
  computed: {
    selected_all() {
      if (this.$store.state.data_header.length > 0 &&
          this.$store.state.select_index.length == this.$store.state.data_header.length){
        return true;
      }else{
        return false;
      }
    }
  },
  methods: {
    set_select_all: function(event) {
      this.$store.commit('set_select_all', {
        'val': event.target.checked,
      });
    },
  }
}
</script>

<style lang='scss' scoped>
#select_all_button {
  font-size: 12px;
  line-height: 26px;
}
</style>
