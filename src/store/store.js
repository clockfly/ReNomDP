import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

const store = new Vuex.Store({
  state: {
    file_id: '',
    files: {},
    interpolate_items: ['None', 'Linear', 'Spline', 'Nearest'],
    select_index: [],
    range: [0, 100],

    row: 0,
    columns: 0,
    data_header: [],
    number_index: undefined,
    hist_data: undefined,
    data_mean: undefined,
    data_var: undefined,
    data_std: undefined,
    data_min: undefined,
    data_25percentile: undefined,
    data_50percentile: undefined,
    data_75percentile: undefined,
    data_max: undefined,
    nan_index: undefined,
    nan_count: undefined,
    nan_ratio: undefined,
    interpolate_list: undefined,

    show_time_series: false,
    loading: false,
  },
  getters: {},

  mutations: {
    set_file_list: function(state, payload) {
      state.files = payload.files;
    },
    set_file_id: function(state, payload) {
      state.file_id = payload.file_id;
    },
    set_load_result: function(state, payload) {
      state.row = payload.data.row;
      state.columns = payload.data.columns;
      state.data_header = payload.data.data_header;
      state.number_index = payload.data.number_index;
      state.number_data = payload.data.number_data;
      state.hist_data = payload.data.hist_data;
      state.data_mean = payload.data.data_mean;
      state.data_var = payload.data.data_var;
      state.data_std = payload.data.data_std;
      state.data_min = payload.data.data_min;
      state.data_25percentile = payload.data.data_25percentile;
      state.data_50percentile = payload.data.data_50percentile;
      state.data_75percentile = payload.data.data_75percentile;
      state.data_max = payload.data.data_max;
      state.nan_index = payload.data.nan_index;
      state.nan_count = payload.data.nan_count;
      state.nan_ratio = payload.data.nan_ratio;
      state.interpolate_list = payload.data.interpolate_list;
    },
    set_loading: function(state, payload) {
      state.loading = payload.loading;
    },
    set_interpolate_all: function(state, payload) {
      if(state.interpolate_list) {
        for(let i=0; i<state.interpolate_list.length; i++) {
          state.interpolate_list.splice(i, 1, payload.val);
        }
      }
    },
    set_interpolate_column: function(state, payload) {
      if(state.hist_data) {
        state.hist_data[payload.index].splice(0, state.hist_data[payload.index].length, ...payload.interpolated_data);
        state.nan_index[payload.index].splice(0, state.nan_index[payload.index].length, ...payload.nan_index);
      }
    },
    set_interpolate_columns: function(state, payload) {
      if(state.hist_data) {
        for(let i=0; i<state.hist_data.length; i++) {
          state.hist_data[i].splice(0, state.hist_data[i].length, ...payload.interpolated_data[i])
          state.nan_index[i].splice(0, state.nan_index[i].length, ...payload.nan_index[i])
        }
      }
    },
    set_interpolate_list: function(state, payload) {
      state.interpolate_list.splice(payload.index, 1, payload.val);
    },
    set_range: function(state, payload) {
      state.range.splice(0, state.range.length, ...payload.val);
    },
    set_select: function(state, payload) {
      const i = state.select_index.indexOf(payload.index);
      if(payload.val && i == -1) {
        state.select_index.push(payload.index);
      }else{
        state.select_index.splice(i, 1);
      }
    },
    set_select_all: function(state, payload) {
      if(state.select_index.length == state.data_header.length) {
        state.select_index.splice(0, state.select_index.length);
      }else{
        state.select_index.splice(0, state.select_index.length);
        for(let i=0; i<state.data_header.length; i++) {
          state.select_index.push(i);
        }
      }
    },
    set_select_index: function(state, payload) {
      state.select_index.splice(0, state.select_index.length);
      state.select_index.push(...payload.val);
    },
    toggle_time_series: function(state, payload) {
      state.show_time_series = !state.show_time_series;
    },
  },

  actions: {
    async load_files(context, payload) {
      context.commit('set_loading', {'loading': true});
      return axios.get('/api/files')
        .then(function(response){
          if(response.data.error_msg) {
            alert(response.data.error_msg);
            context.commit('set_loading', {'loading': false});
            return;
          }
          context.commit('set_file_list', {
            'files': response.data.files,
          });
          context.commit('set_loading', {'loading': false});
        });
    },
    async reload_files(context, payload) {
      await context.dispatch('export_file', {
        'out_file_name': payload.out_file_name,
      });
      await context.dispatch('load_files');
    },
    load_file(context, payload) {
      context.commit('set_loading', {'loading': true});
      const url = '/api/files/' + context.state.file_id
      axios.get(url)
        .then(function(response){
          if(response.data.error_msg) {
            alert(response.data.error_msg);
            context.commit('set_loading', {'loading': false});
            return;
          }

          context.commit('set_load_result', {
            'data': response.data,
          });
          context.commit('set_loading', {'loading': false});
        });
    },
    async export_file(context, payload) {
      context.commit('set_loading', {'loading': true});

      let fd = new FormData();
      fd.append('timeseries', +context.state.show_time_series);
      fd.append('out_file_name', payload.out_file_name);
      fd.append('select_index', context.state.select_index);
      fd.append('interpolate_list', context.state.interpolate_list);
      fd.append('row_range', context.state.range);

      const url = '/api/files/'+context.state.file_id+'/export'
      return axios.post(url, fd).then(function(response){
        if(response.data.error_msg) {
          alert(response.data.error_msg);
        }
        context.commit('set_loading', {'loading': false});
        return;
      });
    },
    interpolate_column(context, payload) {
      context.commit('set_loading', {'loading': true});
      const url = '/api/files/'+context.state.file_id+'/columns/'+payload.index+'/interpolate?interpolate_method='+payload.val
      return axios.get(url).then(function(response){
        if(response.data.error_msg) {
          alert(response.data.error_msg);
          context.commit('set_loading', {'loading': false});
          return;
        }

        context.commit('set_interpolate_list', {
          'index': payload.index,
          'val': payload.val,
        });

        context.commit('set_interpolate_column', {
          'index': payload.index,
          'interpolated_data': response.data.interpolated_data,
          'nan_index': response.data.nan_index,
        })
        context.commit('set_loading', {'loading': false});
        return;
      });
    },
    // interpolate_all(context, payload) {
    //   context.commit('set_loading', {'loading': true});
    //   const url = '/api/files/'+context.state.file_id+'/columns/interpolate?interpolate_method='+payload.val
    //   return axios.get(url).then(function(response){
    //     if(response.data.error_msg) {
    //       alert(response.data.error_msg);
    //       context.commit('set_loading', {'loading': false});
    //       return;
    //     }

    //     context.commit('set_interpolate_columns', {
    //       'interpolated_data': response.data.interpolated_data,
    //       'nan_index': response.data.nan_index,
    //     });
    //     context.commit('set_loading', {'loading': false});
    //     return;
    //   });
    // }
  },
})

export default store
