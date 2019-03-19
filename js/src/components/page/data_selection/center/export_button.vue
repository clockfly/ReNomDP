<template>
  <div id='export_button'>
    <button @click='export_data' :disabled="export_disable">
      <i class="fa fa-pencil-square-o" aria-hidden='true'></i> Export File
    </button>
  </div>
</template>

<script>
export default {
  name: 'ExportButton',
  computed: {
    export_disable() {
      console.log(this.$store.state.select_index)
      if (this.$store.state.select_index && this.$store.state.select_index.length > 0) return false
      return true
    }
  },
  methods: {
    export_data: function() {
      let out_file_name = window.prompt('ファイル名を入力してください。', '');
      if(out_file_name && out_file_name.length > 0){
        this.$store.dispatch('reload_files', {
          'out_file_name': out_file_name,
        });
      }
    },
  }
}
</script>

<style lang='scss' scoped>
#export_button {
}
</style>
