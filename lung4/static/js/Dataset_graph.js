var chartDom = document.getElementById('main');
var myChart = echarts.init(chartDom);
var option;

setTimeout(function () {
  option = {
    color:["#FF8438","#FFF2DA"],
    legend: {
      data: ['LUAD','LUSC'],
      textStyle: {
        color: '#ffffff',
      }
    },
    tooltip: {
      trigger: 'axis',
      showContent: true
    },
    dataset: {
      source: [
        ['Tumor', '训练集', '测试集'],
        ['LUAD', 1500, 3500],
        ['LUSC', 1500, 3500]
      ]
    },
    xAxis: {
      type: 'category',
      axisLabel: {
  　　  show: true,
  　　　color: '#ffffff',
　　 },
      axisLine: {
        lineStyle: {
          color: '#d3d3d3'
        }
      }
    },
    yAxis: {
      gridIndex: 0,
      axisLabel: {
  　　　　show: true,
  　　　　color: '#ffffff',
　　 },
      axisLine: {
        lineStyle: {
          color: '#d3d3d3'
        }
      }
    },
    grid: { top: '55%' },
    series: [
    
      {
        type: 'bar',
        smooth: true,
        seriesLayoutBy: 'row',
        emphasis: { focus: 'series' }
      },
      {
        type: 'bar',
        smooth: true,
        seriesLayoutBy: 'row',
        emphasis: { focus: 'series' }
      },
      {
        type: 'pie',
        id: 'pie',
        radius: '30%',
        center: ['50%', '25%'],
        emphasis: {
          focus: 'self'
        },
        label: {
          formatter: '{b}: {@2012} ({d}%)'
        },
        encode: {
          itemName: '',
          value: '训练集',
          tooltip: ''
        }
      }
    ]
  };
  myChart.on('updateAxisPointer', function (event) {
    const xAxisInfo = event.axesInfo[0];
    if (xAxisInfo) {
      const dimension = xAxisInfo.value + 1;
      myChart.setOption({
        series: {
          id: 'pie',
          label: {
            formatter: '{b}: {@[' + dimension + ']} ({d}%)'
          },
          encode: {
            value: dimension,
            tooltip: dimension
          }
        }
      });
    }
  });
  myChart.setOption(option);
});

option && myChart.setOption(option);
