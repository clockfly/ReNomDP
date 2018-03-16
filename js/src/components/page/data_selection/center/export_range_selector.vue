<template>
  <div id='export_range_selector' v-if='row > 0'>
    <div class='title'>
      Export Area
    </div>

    <div class='range_input'>
      <input type="number" v-model='local_range[0]' @change='change_input($event, 0)'>
    </div>

    <div class='range_slider'>
      <vue-slider :value='range'
        :width='"100%"' :height='4' :dotSize='6'
        :min='0' :max='row-1' :disable='false' :show='true'
        :tooltip='false'
        :bgStyle='{"backgroundColor": "#ccc"}'
        :processStyle='{"backgroundColor": "#999"}'
        @callback='change_range'></vue-slider>
    </div>

    <div class='range_input'>
      <input type="number" v-model='local_range[1]' @change='change_input($event, 1)'>
    </div>
  </div>
</template>

<script>
import {mapState} from 'vuex'
import vueSlider from 'vue-slider-component';

export default {
  name: 'ExportRangeSelector',
  components: {
    'vue-slider': vueSlider,
  },
  data: function() {
    return {
      'local_range': [0, this.row-1],
    }
  },
  computed: mapState(['row', 'range']),
  watch: {
    row: function() {
      this.local_range.splice(0, 2, 0, this.row-1);
    }
  },
  methods: {
    change_range: function(val) {
      this.local_range.splice(0, 2, val[0], val[1]);
      this.$store.commit('set_range', {'val': val});
    },
    change_input: function(event, index) {
      this.$store.commit('set_range_with_index', {
        'index': index,
        'val': parseInt(event.target.value),
      });
    }
  }
}
</script>

<style lang='scss' scoped>
#export_range_selector {
  display: flex;
  display: -webkit-flex;

  .title {
    font-size: 12px;
    line-height: 24px;
  }

  .range_input {
    margin: 0 8px;
  }
  .range_slider {
    width: 200px;
    padding-top: 6px;
  }
}
</style>