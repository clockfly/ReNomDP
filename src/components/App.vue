<template>
  <div id="app">
    <appheader></appheader>
    <router-view></router-view>
    <loading-modal v-if='$store.state.loading'></loading-modal>
  </div>
</template>

<script>
import AppHeader from './common/AppHeader.vue'
import LoadingModal from './common/LoadingModal.vue'

export default {
  name: "app",
  components:{
    'appheader': AppHeader,
    'loading-modal': LoadingModal,
  },
}
</script>

<style lang="scss">
@import url('https://rsms.me/inter/inter-ui.css');
* {
  $background-color: #f8f8f8;

  -webkit-box-sizing: border-box;
  -moz-box-sizing: border-box;
  -o-box-sizing: border-box;
  -ms-box-sizing: border-box;
  box-sizing: border-box;

  font-family: 'Inter UI', sans-serif;
  color: #666;
  background-color: $background-color;
}
select {
  margin: 0;
  padding: 0;
  font-size: 12px;
  color: #666;
  border: 1px solid #ccc;
}
button {
  height: 26px;
  margin: 0;
  padding: 0 24px;
  font-size: 12px;
  line-height: 24px;
  color: #666;
  border: 1px solid #ccc;
  background-color: #f3f3f1;
}
.flex_right {
  margin-left: auto;
}
@for $i from 1 through 15 {
  .margin_left_#{$i*4} {
    margin-left: 4px * $i;
  }
  .margin_right_#{$i*4} {
    margin-right: 4px * $i;
  }
  .margin_top_#{$i*4} {
    margin-top: 4px * $i;
  }
  .margin_bottom_#{$i*4} {
    margin-bottom: 4px * $i;
  }
}
</style>
