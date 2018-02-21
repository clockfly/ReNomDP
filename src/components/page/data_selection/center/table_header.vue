<template>
  <div class="table_header">
    <tr>
      <th>histogram</th>
      <th class='flex_grow_2'>column</th>
      <th>data type</th>
      <th>mean</th>
      <th>var</th>
      <th>std</th>
      <th>min</th>
      <th>25%</th>
      <th>50%</th>
      <th>75%</th>
      <th>max</th>
      <th>nan count</th>
      <th>nan ratio</th>
      <th>interpolate</th>
      <th>select</th>
    </tr>

    <tr class='all_selector_row' v-if='show_time_series && row > 0'>
      <th class='range_selector'>{{range[0]}}〜{{range[1]}}</th>
      <th class='range_bar'>
        <vue-slider :value='range'
          :width='"100%"' :height='4' :dotSize='6'
          :min='0' :max='row-1' :disable='false' :show='true'
          :tooltip='false'
          :bgStyle='{"backgroundColor": "#ccc"}'
          :processStyle='{"backgroundColor": "#0762ad"}'
          @callback='change_range'></vue-slider>
      </th>
    </tr>
  </div>
</template>

<script>
import {mapState} from 'vuex'
import vueSlider from 'vue-slider-component';

export default {
  name: 'TableHeader',
  components: {
    'vue-slider': vueSlider,
  },
  data: function() {
    return {
      range: [0, 0],
    }
  },
  computed: mapState(['row', 'show_time_series']),
  watch: {
    row: function() {
      if(this.row > 0) {
        this.range.splice(0,this.range.length,0,this.row-1);
        this.$store.commit('set_range', {'val': this.range});
      }
    }
  },
  methods: {
    change_range: function(val) {
      this.range.splice(0,this.range.length,...val);
      this.$store.commit('set_range', {'val': val});
    },
  }
}
</script>

<style lang='scss' scoped>
.table_header{
  $all-selector-row-height: 34px;
  $background-color: #f8f8f8;
  $border-color: #cccccc;
  $table-font-size: 10px;

  width: 100%;
  border: none;

  tr {
    border: none;
    border-bottom: 1px solid $border-color;

    th {
      height: $all-selector-row-height;
      padding: 0;
      font-size: $table-font-size;
      font-weight: normal;
      background-color: $background-color;
      text-align: center;
      line-height: $all-selector-row-height;
      border: none;
    }
  }
  .all_selector_row {
    border-bottom: 1px solid $border-color;
    th {
      height: $all-selector-row-height;
      line-height: $all-selector-row-height;
      .select_check_box {
        margin-left: 10px;
        padding-top: 16px;
      }
    }
    .range_selector {
      flex-grow: 1;
      height: 100%;
    }
    .range_bar {
      flex-grow: 14;
      height: 100%;
      padding-top: 12px;
      padding-right: 12px;
    }
  }
  .flex_grow_2 {
    flex-grow: 2;
  }
}
</style>