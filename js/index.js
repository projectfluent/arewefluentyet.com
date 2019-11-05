window.addEventListener("load", main);

async function main() {
  {
    // Manually trigger external font loading to prevent canvas from drawing before the fonts are ready.
    let firaSansRegular = new FontFace('Fira Sans', 'url(./vendor/fira/woff/FiraSans-Regular.woff)', {
      style: 'normal',
      weight: '400'
    });
    let firaSansLight = new FontFace('Fira Sans', 'url(./vendor/fira/woff/FiraSans-Light.woff)', {
      style: 'normal',
      weight: '300'
    });
    let firaSansMedium = new FontFace('Fira Sans', 'url(./vendor/fira/woff/FiraSans-Medium.woff)', {
      style: 'normal',
      weight: '500'
    });
    document.fonts.add(firaSansRegular);
    document.fonts.add(firaSansLight);
    document.fonts.add(firaSansMedium);
    firaSansRegular.load();
    firaSansLight.load();
    firaSansMedium.load();
    await Promise.all([firaSansRegular.loaded, firaSansLight.loaded, firaSansMedium]);
  }

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
    //updateAspectMode();
    //await new Promise((resolve) => setTimeout(resolve, 1000));
  }


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
