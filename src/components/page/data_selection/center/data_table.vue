<template>
  <div id='data_table'>
    <table class='scrollable'>
      <thead>
        <table-header></table-header>
      </thead>

      <tbody>
        <!-- without time series -->
        <table-row-without-ts v-if='!show_time_series'
          v-for='(l, index) in data_header'
          :key='index'
          :index='index'
          :isnam='number_index[index]'
          :histdata='hist_data[index]'
          :colname='l'
          :mean='round(data_mean[index])'
          :vari='round(data_var[index])'
          :std='round(data_std[index])'
          :min='round(data_min[index])'
          :percentile25='round(data_25percentile[index])'
          :percentile50='round(data_50percentile[index])'
          :percentile75='round(data_75percentile[index])'
          :max='round(data_max[index])'
          :nancount='nan_count[index]'
          :nanratio='nan_ratio[index]*100+"%"'
          @select='select'>
        </table-row-without-ts>

        <!-- with time series -->
        <div class='table_row' v-if='show_time_series' v-for='(l, index) in data_header' :key='index'>
          <tr class='timeseries_text_row text_data_row' v-if='!number_index[index]'>
            <td></td>
            <td class='flex_grow_2'>{{l}}</td>
            <td>Text</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>{{ nan_count[index] }}</td>
            <td>{{ round(nan_ratio[index]) }}</td>
            <td>-</td>
            <td>
              <div class='input-group select_check_box'>
                <input type='checkbox' :id='"select"+index' :value='index' v-model='select_index'>
                <label :for='"select"+index'></label>
              </div>
            </td>
          </tr>

          <tr class='timeseries_text_row' v-if='number_index[index]'>
            <td></td>
            <td class='flex_grow_2'>{{l}}</td>
            <td>Number</td>
            <td>{{ round(data_mean[index]) }}</td>
            <td>{{ round(data_var[index]) }}</td>
            <td>{{ round(data_std[index]) }}</td>
            <td>{{ round(data_min[index]) }}</td>
            <td>{{ round(data_25percentile[index]) }}</td>
            <td>{{ round(data_50percentile[index]) }}</td>
            <td>{{ round(data_75percentile[index]) }}</td>
            <td>{{ round(data_max[index]) }}</td>
            <td>{{ nan_count[index] }}</td>
            <td>{{ round(nan_ratio[index]) }}</td>
            <td>{{ interpolate_items[interpolate_list[index]] }}</td>
            <td>
              <div class='input-group select_check_box'>
                <input type='checkbox' :id='"select"+index' :value='index' v-model='select_index'>
                <label :for='"select"+index'></label>
              </div>
            </td>
          </tr>

          <tr class='timeseries_graph_row' v-if='number_index[index]'>
            <td class="histogram">
              <histogram :id='index' :histdata='hist_data[index]'></histogram>
            </td>
            <td class='timeseries_graph'>
              <timeseries :id='index' :timedata='hist_data[index]' :nanindex='nan_index[index]'></timeseries>
            </td>
          </tr>
        </div>
      </tbody>
    </table>
  </div>
</template>

<script>
import {mapState} from 'vuex'
import vueSlider from 'vue-slider-component';
import Histogram from './histogram.vue'
import TableHeader from './table_header.vue'
import TableRowWithoutTimeseries from './table_row_without_timeseries.vue'
import TimeSeries from './timeseries.vue'

export default {
  name: 'DataTable',
  components: {
    'histogram': Histogram,
    'table-header': TableHeader,
    'table-row-without-ts': TableRowWithoutTimeseries,
    'timeseries': TimeSeries,
    'vue-slider': vueSlider,
  },
  data: function() {
    return {
      range: [0, 0],
    }
  },
  computed: {
    ...mapState([
      'row',
      'interpolate_items',
      'show_time_series',
      'number_index',
      'number_data',
      'hist_data',
      'data_header',
      'data_mean',
      'data_var',
      'data_std',
      'data_min',
      'data_25percentile',
      'data_50percentile',
      'data_75percentile',
      'data_max',
      'nan_index',
      'nan_count',
      'nan_ratio',
      'interpolate_list']),
    select_index: {
      get: function() {
        return this.$store.state.select_index;
      },
      set: function(val) {
        this.$store.commit('set_select_index', {'val': val});
      }
    },
  },
  watch: {
    row: function() {
      if(this.row > 0) {
        this.range.splice(0,this.range.length,0,this.row-1);
        this.$store.commit('set_range', {'val': this.range});
      }
    }
  },
  methods: {
    round: function(val) {
      return Math.round(val*100)/100;
    },
    set_interpolate_list: function(event, index) {
      this.$store.dispatch('interpolate_column', {
        'index': index,
        'val': parseInt(event.target.value),
      });
    },
    select: function(value) {
      this.$store.commit('set_select', {
        'index': value.index,
        'val': value.val,
      });
    }
  }
}
</script>

<style lang='scss' scoped>
#data_table {
  $background-color: #f8f8f8;
  $border-color: #cccccc;
  $table-row-height: 92px;
  $all-selector-row-height: 34px;
  $timeseries-text-row-height: 40px;
  $table-font-size: 10px;

  width: 100%;
  height: 100%;
  padding: 0 48px;

  table.scrollable {
    padding: 0;
  }
  table {
    max-height: calc(100vh - 150px);
    thead {
      border: none;
    }

    tbody {
      border: none;
      tr {
        border: none;
        border-bottom: 1px solid $border-color;

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
      }
      .table_row {
        width: 100%;

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
      }
    }
    .flex_grow_2 {
      flex-grow: 2;
    }
  }
}
</style>