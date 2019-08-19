function getDatasetByLabel(chart, label) {
  for (let i in chart.data.datasets) {
    let dataset = chart.data.datasets[i];
    if (dataset.label == label) {
      return dataset;
    }
  }
  return null;
}

function getCategoryForLabel(label) {
  for (let cat in State.theme.categories.labels) {
    if (State.theme.categories.labels[cat] === label) {
      return cat;
    }
  }
  return null;
}

function getBarPosition(chart, index) {
  let x;
  let y;
  if (Page.getCategoriesBar()[0] === null) {
    let meta = chart.getDatasetMeta(0);
    x = meta.data[index]._model.x;
    y = chart.chartArea.bottom;
  } else {
    let idx0 = Page.getCategoriesBar()[0];
    let meta = chart.getDatasetMeta(idx0);
    x = meta.data[index]._model.x;
    y = meta.data[index]._model.y;
  }
  let meta2 = chart.getDatasetMeta(Page.getCategoriesBar()[1]);
  let x2 = meta2.data[index]._model.x;
  let y2 = meta2.data[index]._model.y;
  return [[x, y], [x2, y2]];
}

function getBarCategories(start = 0, end = 0) {
  let result = [];
  for (let idx in Page.getCategories()) {
    if ((Page.getCategories[0] === null || idx >= Page.getCategoriesBar()[0] + start) && (Page.getCategoriesBar()[1] === null || idx <= Page.getCategoriesBar()[1] + end)) {
      result.push(Page.getCategories()[idx]);
    }
  }
  return result;
}