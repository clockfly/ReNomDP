<template>
  <div class="table_header">
    <tr>
      <th>histogram</th>
      <th class='flex_grow_2'>column</th>
      <th :class='{active: selected_column === "dtype"}'
        @click='select_column("dtype")'>data type</th>
      <th :class='{active: selected_column === "mean"}'
        @click='select_column("mean")'>mean</th>
      <th :class='{active: selected_column === "var"}'
        @click='select_column("var")'>var</th>
      <th :class='{active: selected_column === "std"}'
        @click='select_column("std")'>std</th>
      <th :class='{active: selected_column === "min"}'
        @click='select_column("min")'>min</th>
      <th :class='{active: selected_column === "25%"}'
        @click='select_column("25%")'>25%</th>
      <th :class='{active: selected_column === "50%"}'
        @click='select_column("50%")'>50%</th>
      <th :class='{active: selected_column === "75%"}'
        @click='select_column("75%")'>75%</th>
      <th :class='{active: selected_column === "max"}'
        @click='select_column("max")'>max</th>
      <th :class='{active: selected_column === "nan_count"}'
        @click='select_column("nan_count")'>nan count</th>
      <th :class='{active: selected_column === "nan_ratio"}'
        @click='select_column("nan_ratio")'>nan ratio</th>
      <th>interpolate</th>
      <th>select</th>
    </tr>

    <tr class='all_selector_row' v-if='show_time_series && row > 0'>
      <th class='range_selector'>{{range[0]}}〜{{range[1]}}</th>
      <th class='range_bar'>
        <vue-slider v-if='row > 999' :value='timeseries_range'
          :width='"100%"' :height='4' :dotSize='6'
          :min='0' :max='row-1' :disable='false' :show='true'
          :tooltip='false'
          :style='{"padding": 0}'
          :bgStyle='{"backgroundColor": "#f8f8f8"}'
          :processStyle='{"backgroundColor": "#f8f8f8"}'
          :sliderStyle='{"width": 0, "height": 0,
            "border": "4px solid transparent",
            "border-top": "4px solid #999",
            "box-shadow": "0px 0px",
            "border-radius": "0" }'
          @callback='change_timeseries_range'></vue-slider>

        <vue-slider :value='range'
          :width='"100%"' :height='4' :dotSize='6'
          :min='0' :max='row-1' :disable='false' :show='true'
          :tooltip='false'
          :style='{"z-index": 999}'
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
  computed: mapState(['row', 'show_time_series', 'range',
    'timeseries_range', 'selected_column']),
  methods: {
    change_range: function(val) {
      this.$store.commit('set_range', {'val': val});
    },
    change_timeseries_range: function(val) {
      this.$store.commit('set_timeseries_range', {'val': val});
    },
    select_column: function(name) {
      this.$store.commit('set_select_column_name', {'name': name});
    }
  }
}
</script>

<style lang='scss' scoped>
.table_header{
  $all-selector-row-height: 34px;
  $background-color: #f8f8f8;
  $background-color-active: #f0f0f0;
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
      padding-top: 8px;
      padding-right: 12px;
    }
  }
  .flex_grow_2 {
    flex-grow: 2;
  }
  .active {
    background-color: $background-color-active;
  }
}
</style>