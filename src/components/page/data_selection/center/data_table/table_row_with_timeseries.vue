<template>
  <div class="table_row">
    <tr class='timeseries_text_row text_data_row' v-if='!isnum'>
      <td></td>
      <td class='flex_grow_2'>{{ colname }}</td>
      <td>Text</td>
      <td>-</td>
      <td>-</td>
      <td>-</td>
      <td>-</td>
      <td>-</td>
      <td>-</td>
      <td>-</td>
      <td>-</td>
      <td>{{ nancount }}</td>
      <td>{{ nanratio }}</td>
      <td>-</td>
      <td>
        <div class='input-group select_check_box'>
          <input type='checkbox' :id='"select"+index' :checked='selected' @change='select'>
          <label :for='"select"+index'></label>
        </div>
      </td>
    </tr>

    <tr class='timeseries_text_row' v-if='isnum'>
      <td></td>
      <td class='flex_grow_2'>{{ colname }}</td>
      <td>Number</td>
      <td>{{ mean }}</td>
      <td>{{ vari }}</td>
      <td>{{ std }}</td>
      <td>{{ min }}</td>
      <td>{{ percentile25 }}</td>
      <td>{{ percentile50 }}</td>
      <td>{{ percentile75 }}</td>
      <td>{{ max }}</td>
      <td>{{ nancount }}</td>
      <td>{{ nanratio }}</td>
      <td>{{ interpolate }}</td>
      <td>
        <div class='input-group select_check_box'>
          <input type='checkbox' :id='"select"+index' :checked='selected' @change='select'>
          <label :for='"select"+index'></label>
        </div>
      </td>
    </tr>

    <tr class='timeseries_graph_row' v-if='isnum'>
      <td class="histogram">
        <histogram :id='index' :histdata='histdata'></histogram>
      </td>
      <td class='timeseries_graph'>
        <timeseries :id='index'
          :timedata='histdata.slice(timeseries_range[0], timeseries_range[1])'
          :nanindex='nanindex.slice(timeseries_range[0], timeseries_range[1])'
          :miny='Math.min(...histdata)'
          :maxy='Math.max(...histdata)'>
        </timeseries>
      </td>
    </tr>
  </div>
</template>

<script>
import {mapState} from 'vuex'
import Histogram from './histogram.vue'
import TimeSeries from './timeseries.vue'

export default {
  name: 'TableRowWithTimeseries',
  components: {
    'histogram': Histogram,
    'timeseries': TimeSeries,
  },
  props: ['index', 'isnum', 'histdata', 'colname', 'mean',
          'vari', 'std', 'min', 'percentile25',
          'percentile50', 'percentile75',
          'max', 'nancount', 'nanratio', 'nanindex',
          'interpolate', 'selected'],
  computed: mapState(['timeseries_range']),
  methods: {
    select: function(event) {
      const value = {
        'val': event.target.checked,
        'index': this.index,
      }
      this.$emit('select', value);
    }
  },
  created: function() {
    this.$store.commit('set_loading', {'loading': true});
  },
  mounted: function() {
    this.$store.commit('set_loading', {'loading': false});
  }
}
</script>

<style lang='scss' scoped>
.table_row {
  $table-row-height: 92px;
  $timeseries-text-row-height: 40px;
  $background-color: #f8f8f8;
  $border-color: #cccccc;
  $table-font-size: 10px;

  width: 100%;
  border: none;
  border-bottom: 1px solid $border-color;

  .timeseries_text_row {
    border: none;
    td {
      height: $timeseries-text-row-height;
      line-height: $timeseries-text-row-height;
    }
  }
  .text_data_row {
    border-bottom: 1px solid $border-color;
  }
  .timeseries_graph_row {
    td {
      height: $table-row-height;
      line-height: $table-row-height;
    }
  }

  td {
    height: $table-row-height;
    padding: 0;
    font-size: $table-font-size;
    text-align: center;
    line-height: $table-row-height;
    border: none;

    select{
      padding-left: 4px;
      padding-right: 4px;
      font-size: $table-font-size;
    }

    .select_check_box {
      margin-left: 10px;
      padding-top: 18px;
      input[type='checkbox']+label{
        margin-top: 10px;
      }
      input[type='checkbox']+label:before {
        bottom: 0.55rem;
        left: 0.5rem;
        width: $table-font-size;
        height: $table-font-size;
      }
      input[type='checkbox']+label:after {
        left: 0.55rem;
        width: $table-font-size;
        height: $table-font-size;
        background-color: #666;
      }
    }

    .histogram_area {
      margin-top: 10px;
    }
  }
  .histogram {
    flex-grow: 1;
    height: 100%;
  }
  .timeseries_graph {
    flex-grow: 14;
    height: 100%;
  }

  .flex_grow_2 {
    flex-grow: 2;
  }
}
</style>