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
  const idx0 = Page.getCategoriesBar()[0];
  const meta = chart.getDatasetMeta(idx0 ?? 0);
  if (index >= meta.data.length) index = meta.data.length - 1;
  const model = meta.data[index]._model;
  const x = model.x;
  const y = idx0 === null ? chart.chartArea.bottom : model.y;

  const idx2 = Page.getCategoriesBar()[1];
  const meta2 = chart.getDatasetMeta(idx2);
  if (index >= meta2.data.length) index = meta2.data.length - 1;
  const model2 = meta2.data[index]._model;
  const x2 = model2.x;
  const y2 = model2.y;

  return [
    [x, y],
    [x2, y2],
  ];
}

function getBarCategories(start = 0, end = 0) {
  let result = [];
  for (let idx in Page.getCategories()) {
    if (
      (Page.getCategories[0] === null ||
        idx >= Page.getCategoriesBar()[0] + start) &&
      (Page.getCategoriesBar()[1] === null ||
        idx <= Page.getCategoriesBar()[1] + end)
    ) {
      result.push(Page.getCategories()[idx]);
    }
  }
  return result;
}
