<template>
  <div id='center'>
    <div class='file_summary_area margin_top_16'>
      <file-loader class='margin_left_48'></file-loader>
      <file-summary class='margin_left_48'></file-summary>
      <export-button class='margin_right_48 flex_right'></export-button>
    </div>

    <div class='data_table_global_area margin_top_16'>
      <time-series-button class='margin_left_48'></time-series-button>
      <select-all-button class='margin_right_48 flex_right'></select-all-button>
    </div>

    <div class='data_table_area margin_top_16'>
      <data-table></data-table>
    </div>
  </div>
</template>

<script>
import DataTable from './data_table.vue'
import ExportButton from './export_button.vue'
import FileLoader from './file_loader.vue'
import FileSummary from './file_summary.vue'
import SelectAllButton from './select_all_button.vue'
import TimeSeriesButton from './time_series_button.vue'

export default {
  name: 'DataSelectionCenter',
  components: {
    'data-table': DataTable,
    'export-button': ExportButton,
    'file-loader': FileLoader,
    'file-summary': FileSummary,
    'select-all-button': SelectAllButton,
    'time-series-button': TimeSeriesButton,
  }
}
</script>

<style lang='scss' scoped>
#center {
  $header-height: 44px;
  width: 100%;
  max-width: 1280px;
  height: calc(100vh - #{$header-height});
  margin: 0 auto;
  padding: 0;


  .file_summary_area, .data_table_global_area {
    display: -webkit-flex;
    display: flex;

    width: 100%;
    height: 26px;
  }

  .data_table_area {
    width: 100%;
    height: calc(100% - 26px*2 - 16px*4);
  }
}
</style>