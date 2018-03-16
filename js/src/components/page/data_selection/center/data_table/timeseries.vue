<template>
  <div :id="'time'+id" class='timeseries' v-if='timedata'>
    <div :id="'interpolate_selector'+id" class='interpolate_selector'
         :style="'top:'+interpolate_selector_top+'px; left:'+interpolate_selector_left+'px;'"
         v-if='show_interpolate_selector'>
      <div class='item' :class='{active: interpolate_list[id] == index}'
           v-for='(item, index) in interpolate_items' :key='index'
           @click='select_interpolate(index)'>
        {{ item }}
      </div>
    </div>
  </div>
</template>

<script>
import {mapState} from 'vuex'

export default {
  name: "TimeSeries",
  props: ["id", "timedata", 'nanindex', 'interpolateindex', 'miny', 'maxy'],
  data: function() {
    return {
      'show_interpolate_selector': false,
      'interpolate_selector_top': 0,
      'interpolate_selector_left': 0,
      'height': 48,
      'margin': {
        'top': 12,
        'bottom': 12,
        'left': 10,
        'right': 10
      },
      'has_null': false,
    }
  },
  computed: {
    ...mapState(['range', 'timeseries_range',
      'interpolate_items', 'interpolate_list']),
    timeseries_element() {
      return d3.select('#time'+this.id);
    },
    interpolate_line() {
      const self = this;
      return d3.line()
        .x(function(d) { return self.scale_x(d.x); })
        .y(function(d) { return self.scale_y(d.y); });
    },
    line() {
      const self = this;
      return d3.line()
        .defined(function(d, i) { return !self.nanindex[i]; })
        .x(function(d) { return self.scale_x(d.x); })
        .y(function(d) { return self.scale_y(d.y); });
    },
    line_data() {
      let data = []
      let d = {}
      let has_null = false;
      for(let i in this.timedata) {
        if(this.timedata[i] == ''){
          d = { 'x': +i+this.min_axis_x, 'y': null };
          data.push(d);
          has_null = true;
        }else{
          d = { 'x': +i+this.min_axis_x, 'y': parseFloat(this.timedata[i]) };
          data.push(d);
        }
      }
      this.has_null = has_null;
      return data;
    },
    min_axis_x() {
      return this.timeseries_range[0];
    },
    max_axis_x() {
      return this.timeseries_range[1];
    },
    scale_x() {
      const width = this.svg_width - this.margin.left - this.margin.right;
      return d3.scaleLinear()
        .domain([this.min_axis_x, this.max_axis_x])
        .rangeRound([0, width]);
    },
    scale_y() {
      return d3.scaleLinear()
        .domain([this.miny, this.maxy])
        .rangeRound([this.height, 0]);
    },
    svg_height() {
      return this.height + this.margin.top + this.margin.bottom
    },
    svg_width() {
      return this.timeseries_element._groups[0][0].clientWidth;
    }
  },
  mounted: function(){
    this.draw_graph();
  },
  watch: {
    timedata: function() {
      this.update_graph();
    },
    range: function() {
      this.update_graph();
    }
  },
  methods: {
    draw_line: function(svg, data, line, color) {
      svg.append('path')
        .datum(data)
        .attr('style', function(d) {
          return 'fill: none; stroke: '+color+';'})
        .attr('d', line);
    },
    draw_interpolate_area(svg) {
      let interpolated_data = []
      for(let i of this.interpolateindex){
        // 軸にグレーの矩形をかぶせる
        svg.append('rect')
          .attr('x', this.scale_x(parseInt(i[0])))
          .attr('y', this.height-5)
          .attr('width', this.scale_x(parseInt(i[i.length-1])) - this.scale_x(parseInt(i[0])))
          .attr('height', 10)
          .attr('fill', '#aaa')
          .attr('opacity', 0.3)
          .attr('class', 'nan_area_rect');

        for(let val of i) {
          if(val >= this.timeseries_range[0] && val <= this.timeseries_range[1]){
            interpolated_data.push(this.line_data[parseInt(val)-this.timeseries_range[0]]);
          }
        }

        if(!this.has_null){
          this.draw_line(svg, interpolated_data, this.interpolate_line, '#ef8200');
          interpolated_data = [];
        }
      }
    },
    draw_axis: function(svg) {
      svg.append('g')
        .attr('class', 'axis')
        .attr('transform', 'translate(0,' + this.height + ')')
        .call(d3.axisBottom(this.scale_x));
    },
    draw_export_line: function(svg) {
      let self = this;
      let line = d3.line()
        .x(function(d) { return self.scale_x(d.x); })
        .y(function(d) { return d.y; });

      let range0 = [{'x': this.range[0], 'y': 0}, {'x': this.range[0], 'y': 48}]
      let range1 = [{'x': this.range[1], 'y': 0}, {'x': this.range[1], 'y': 48}]

      svg.append('path')
        .datum(range0)
        .attr('style', function(d) {
          return 'fill: none; stroke: #f00; stroke-dasharray: 5 2;'})
        .attr('d', line);
      svg.append('path')
        .datum(range1)
        .attr('style', function(d) {
          return 'fill: none; stroke: #f00; stroke-dasharray: 5 2;'})
        .attr('d', line);
    },
    draw_graph: function() {
      // console.time('time_draw_row');
      const self = this;
      if(self.timedata) {
        let svg = self.timeseries_element.append('svg')
          .attr('width', self.svg_width)
          .attr('height', self.svg_height)
          .on('click', function() {
            let mouse = d3.mouse(this);
            self.interpolate_selector_top = 0;
            self.interpolate_selector_left = mouse[0];
            self.show_interpolate_selector = !self.show_interpolate_selector;
          });

        this.draw_line(svg, this.line_data, this.line, '#5c94aa');
        if(this.interpolateindex.length > 0){
          this.draw_interpolate_area(svg);
        }
        this.draw_axis(svg);
        this.draw_export_line(svg);
      }
      // console.timeEnd('time_draw_row');
    },
    update_graph: function() {
      // console.time('update_row');
      let svg = this.timeseries_element.select('svg');
      svg.selectAll('path').remove();
      svg.selectAll('rect').remove();
      svg.selectAll('g').remove();

      this.draw_line(svg, this.line_data, this.line, '#5c94aa');
      if(this.interpolateindex.length > 0){
        this.draw_interpolate_area(svg);
      }
      this.draw_axis(svg);
      this.draw_export_line(svg);
      // console.timeEnd('update_row');
    },
    select_interpolate(val) {
      this.$store.dispatch('interpolate_column', {
        'index': this.id,
        'val': val,
      });
      this.show_interpolate_selector = false;
    }
  }
}
</script>

<style lang='scss'>
$axis-line-color: #cccccc;
$axis-text-color: #999999;

.timeseries {
  width: 100%;
  height: 100%;
  position: relative;

  .interpolate_selector {
    position: absolute;
    padding: 4px 12px;
    background-color: #666666;
    .item {
      color: #cccccc;
    }
    .active {
      color: #ffffff;
    }
  }

  svg {
    margin-top: 6px;
    cursor: pointer;
  }
  .axis line {
    stroke: $axis-line-color;
  }
  .axis path {
    stroke: $axis-line-color;
    stroke-width: 0.5;
  }
  .axis text {
    font-size: 8px;
    fill: $axis-text-color;
  }
}
</style>