main();

async function main() {
  layout();
  updateAspectMode();

  let ms = Page.getActiveMilestone();
  let chart = create_chart(
    "#main-chart > canvas",
    await prepare_data(`./data/${ms.code}/progress.json`)
  );
  State.charts.push(chart);

  Page.updateMilestones();
  Page.setListLinkTarget();

  if (State.dashboard) {
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }

  await document.fonts.ready;

  document.body.style.display = "block";
  window.addEventListener("resize", updateAspectMode);
}

function create_chart(selector, { all_labels, month_labels, data }) {
  // This hack allows us to draw shadow for the circles
  let draw = Chart.controllers.line.prototype.draw;
  Chart.controllers.line = Chart.controllers.line.extend({
    draw: function(ease) {
      draw.call(this, ease);
      let ctx = this.chart.chart.ctx;
      let _stroke = ctx.stroke;
      ctx.stroke = function() {
        ctx.save();
        if (this.strokeStyle == State.theme.points.color) {
          ctx.shadowColor = State.theme.points.shadow.color;
          ctx.shadowBlur = State.theme.points.shadow.blur;
          ctx.shadowOffsetX = State.theme.points.shadow.offsetX;
          ctx.shadowOffsetY = State.theme.points.shadow.offsetY;
        }
        _stroke.apply(this, arguments);
        ctx.restore();
      };
    }
  });

  let ctx = document.querySelector(selector).getContext("2d");
  return get_chart(ctx, data, all_labels, month_labels);
}
