<template>
  <div id='data_table'>
    <table class='scrollable'>
      <thead>
        <tr>
          <th>histogram</th>
          <th class='grow_2'>column</th>
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
      </thead>

      <tbody>
        <!-- without time series -->
        <div class="table_row" v-if='!show_time_series' v-for='(l, index) in data_header' :key='index'>
          <tr>
            <td>
              <div class="histogram_area" v-if='number_index[index]'>
                <histogram :id='index' :histdata='hist_data[index]'></histogram>
              </div>
            </td>
            <td class='grow_2'>{{l}}</td>
            <td>
              <span v-if='number_index[index]'>Number</span>
              <span v-if='!number_index[index]'>Text</span>
            </td>
            <td>
              <span v-if='number_index[index]'>{{ round(data_mean[index]) }}</span>
              <span v-if='!number_index[index]'>-</span>
            </td>
            <td>
              <span v-if='number_index[index]'>{{ round(data_var[index]) }}</span>
              <span v-if='!number_index[index]'>-</span>
            </td>
            <td>
              <span v-if='number_index[index]'>{{ round(data_std[index]) }}</span>
              <span v-if='!number_index[index]'>-</span>
            </td>
            <td>
              <span v-if='number_index[index]'>{{ round(data_min[index]) }}</span>
              <span v-if='!number_index[index]'>-</span>
            </td>
            <td>
              <span v-if='number_index[index]'>{{ round(data_25percentile[index]) }}</span>
              <span v-if='!number_index[index]'>-</span>
            </td>
            <td>
              <span v-if='number_index[index]'>{{ round(data_50percentile[index]) }}</span>
              <span v-if='!number_index[index]'>-</span>
            </td>
            <td>
              <span v-if='number_index[index]'>{{ round(data_75percentile[index]) }}</span>
              <span v-if='!number_index[index]'>-</span>
            </td>
            <td>
              <span v-if='number_index[index]'>{{ round(data_max[index]) }}</span>
              <span v-if='!number_index[index]'>-</span>
            </td>
            <td>
              <span v-if='number_index[index]'>{{ nan_count[index] }}</span>
              <span v-if='!number_index[index]'>-</span>
            </td>
            <td>
              <span v-if='number_index[index]'>{{ round(nan_ratio[index]) }}</span>
              <span v-if='!number_index[index]'>-</span>
            </td>
            <td>
              <span>-</span>
            </td>
            <td>
              <div class='input-group select_check_box'>
                <input type='checkbox' :id='"select"+index' :value='index' v-model='select_index'>
                <label :for='"select"+index'></label>
              </div>
            </td>
          </tr>
        </div>

        <!-- with time series -->
        <div class='table_row' v-if='show_time_series' v-for='(l, index) in data_header' :key='index'>
          <tr class='timeseries_text_row text_data_row' v-if='!number_index[index]'>
            <td></td>
            <td class='grow_2'>{{l}}</td>
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
            <td class='grow_2'>{{l}}</td>
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
import TimeSeries from './timeseries.vue'

export default {
  name: 'DataTable',
  components: {
    'histogram': Histogram,
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
    change_range: function(val) {
      this.range.splice(0,this.range.length,...val);
      this.$store.commit('set_range', {'val': val});
    },
    round: function(val) {
      return Math.round(val*100)/100;
    },
    set_interpolate_list: function(event, index) {
      this.$store.dispatch('interpolate_column', {
        'index': index,
        'val': parseInt(event.target.value),
      });
    },
    // set_interpolate_all: function(event) {
    //   this.$store.commit('set_interpolate_all', {
    //     'val': parseInt(event.target.value),
    //   });
    //   this.$store.dispatch('interpolate_all', {
    //     'val': parseInt(event.target.value),
    //   });
    // },
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
    .grow_2 {
      flex-grow: 2;
    }
  }
}
</style>