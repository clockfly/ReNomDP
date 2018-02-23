<template>
  <div id='export_button'>
    <button @click='export_data'>
      <i class="fa fa-pencil-square-o" aria-hidden='true'></i> Export File
    </button>
  </div>
</template>

<script>
export default {
  name: 'ExportButton',
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