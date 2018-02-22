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
  props: ["id", "timedata", 'nanindex', 'miny', 'maxy'],
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
    }
  },
  computed: {
    ...mapState(['range', 'timeseries_range', 'interpolate_items', 'interpolate_list']),
    timeseries_element() {
      return d3.select('#time'+this.id);
    },
    has_null() {
      return this.nanindex.length != this.timedata.length;
    },
    inverse_line() {
      const self = this;
      return d3.line()
        .x(function(d) { return self.scale_x(d.x); })
        .y(function(d) { return self.scale_y(d.y); });
    },
    line() {
      const self = this;
      return d3.line()
        .defined(function(d,i) { return !self.nanindex[i]; })
        .x(function(d, i) { return self.scale_x(self.min_axis_x + i); })
        .y(function(d) { return self.scale_y(d); });
    },
    line_data() {
      const self = this;
      let data = d3.range(self.time_data_with_null.length).map(function(d) {
        return self.time_data_with_null[d];
      });
      return data;
    },
    min_axis_x() {
      return this.timeseries_range[0];
    },
    max_axis_x() {
      return this.timeseries_range[1];
    },
    time_data_with_null() {
      let timedata = [];
      if(this.timedata){
        timedata.push(...this.timedata);
        for(let i=0; i<this.nanindex.length; i++) {
          if(this.nanindex[i] && this.has_null) {
            timedata.splice(i, 0, null);
          }
        }
      }
      return timedata;
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
    draw_rect: function(svg) {
      svg.append('rect')
        .attr('x', this.scale_x(this.range[0]))
        .attr('y', 0)
        .attr('width', this.scale_x(this.range[1]) - this.scale_x(this.range[0]))
        .attr('height', this.height)
        .attr('fill', '#ddd')
        .attr('opacity', 0.3);
    },
    draw_interpolate_area(svg) {
      let last_value = false;
      let nan_start = 0;
      let nan_end = 0;
      let interpolated_data = []
      let d = {}
      for(let i in this.nanindex) {
        if(this.nanindex[i] && !last_value) {
          // 欠損領域の開始
          if(i > 0){
            d = { 'x': i-1, 'y': this.line_data[i-1] };
            interpolated_data.push(d);
          }

          d = { 'x': i, 'y': this.line_data[i] };
          interpolated_data.push(d);
          nan_start = i-1;
          last_value = true;
        }else if(last_value) {
          // 欠損領域内
          d = { 'x': i, 'y': this.line_data[i] };
          interpolated_data.push(d);

          if(!this.nanindex[i]) {
            // 欠損領域の終了
            nan_end = +i;
            last_value = false;

            // 軸にグレーの矩形をかぶせる
            svg.append('rect')
              .attr('x', this.scale_x(nan_start))
              .attr('y', this.height-5)
              .attr('width', this.scale_x(nan_end) - this.scale_x(nan_start))
              .attr('height', 10)
              .attr('fill', '#aaa')
              .attr('opacity', 0.3)
              .attr('class', 'nan_area_rect');

            if(!this.has_null) {
              this.draw_line(svg, interpolated_data, this.inverse_line, '#ef8200');
              interpolated_data = []
            }
          }
        }
      }
    },
    draw_axis: function(svg) {
      svg.append('g')
        .attr('class', 'axis')
        .attr('transform', 'translate(0,' + this.height + ')')
        .call(d3.axisBottom(this.scale_x));
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
        // this.draw_rect(svg);
        this.draw_interpolate_area(svg);
        this.draw_axis(svg);
      }
      // console.timeEnd('time_draw_row');
    },
    update_graph: function() {
      let svg = this.timeseries_element.select('svg');
      svg.selectAll('path').remove();
      svg.selectAll('rect').remove();
      svg.selectAll('g').remove();

      this.draw_line(svg, this.line_data, this.line, '#5c94aa');
      this.draw_interpolate_area(svg);
      this.draw_axis(svg);
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