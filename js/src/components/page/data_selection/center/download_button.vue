<template>
  <div id='download_button'>
    <button @click='download'>
      <i class="fa fa-download" aria-hidden='true'></i> Download File
    </button>
  </div>
</template>

<script>
import {mapState} from 'vuex'

export default {
  name: 'DownloadButton',
  computed: mapState(['file_id']),
  methods: {
    download: function() {
      if(window.confirm('ダウンロードしますか？')){
        if(this.file_id != ''){
          const url = '/api/files/'+this.file_id+'/download';
          window.open(url, "__blank");
        }
      }
    },
  }
}
</script>

<style lang='scss' scoped>
#download_button {
}
</style>