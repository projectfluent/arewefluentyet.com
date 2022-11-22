function get_chart(ctx, data, all_labels, month_labels) {
  return new Chart(ctx, {
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      title: {
        display: true,
        position: Page.getTitlePosition(),
        text: Page.getActiveMilestone().title,
        fontStyle: State.theme.title.font.weight,
        fontSize: Page.getTitleFontSize(),
        fontFamily: State.theme.main.font.family,
        fontColor: State.theme.main.font.color,
      },
      animation: {
        duration: 0,
      },
      scales: {
        yAxes: [
          {
            stacked: true,
            id: "main-y-axis",
            display: true,
            gridLines: {
              display: false,
            },
            ticks: {
              padding: Page.getYAxisPadding(),
              fontStyle: State.theme.main.font.weight,
              fontSize: Page.getChartFontSize(),
              fontFamily: State.theme.main.font.family,
              fontColor: State.theme.axes.font.color,
            },
          },
          {
            stacked: true,
            id: "background-y-axis",
            display: false,
          },
        ],
        xAxes: [
          {
            display: true,
            id: "main-x-axis",
            barThickness: State.theme.bar.width,
            type: "time",
            time: {
              unit: "quarter",
              stepSize: 1,
            },
            labels: State.dashboard ? month_labels : all_labels,
            ticks: {
              lineHeight: 2.4,
              fontStyle: State.theme.main.font.weight,
              fontSize: Page.getChartFontSize(),
              fontFamily: State.theme.main.font.family,
              fontColor: State.theme.axes.font.color,
            },
            gridLines: {
              display: false,
            },
          },
          {
            display: false,
            id: "background-x-axis",
            type: "time",
            time: {
              unit: "quarter",
              stepSize: 1,
            },
          },
        ],
      },
      tooltips: {
        enabled: false,
      },
      hover: State.dashboard
        ? false
        : {
            mode: "index",
            axis: "x",
            intersect: false,
            animationDuration: 0,
            onHover: function (event, elements) {
              if (elements.length == 0) {
                return;
              }
              let index = elements[0]._index;
              let ctx = this.chart.ctx;
              let [[x, y], [x2, y2]] = getBarPosition(this.chart, index);

              var boxHeight =
                (Page.getActiveMilestone().categories.length + 1) * 22.4;
              var boxHeightHalf = boxHeight / 2;
              let distance = Math.abs(y2 - y);
              if (boxHeight >= distance) {
                return;
              }

              let distanceHalf = distance / 2;
              ctx.save();
              (ctx.lineWith = State.theme.bar.width),
                (ctx.strokeStyle = State.theme.bar.color),
                ctx.beginPath();
              ctx.moveTo(x, y);
              ctx.lineTo(x, y - distanceHalf + boxHeightHalf);
              ctx.stroke();

              ctx.beginPath();
              ctx.moveTo(x, y - distanceHalf - boxHeightHalf);
              ctx.lineTo(x, y - distance);
              ctx.stroke();

              ctx.restore();
            },
          },
      elements: {
        point: {
          borderColor: State.theme.points.color,
          borderWidth: State.theme.points.border.width,
          hoverBorderWidth: State.theme.points.border.width,
          hoverRadius: State.theme.points.radius,
          hoverBorderColor: State.theme.points.color,
          radius: State.theme.points.radius,
        },
      },
      legend: {
        display: Page.shouldDisplayLegend(),
        position: "bottom",
        labels: {
          filter: function (l) {
            return Page.getActiveMilestone().categories.includes(l.text);
          },
        },
      },
    },
  });
}
