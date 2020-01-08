const activeMilestone = new URL(document.location).searchParams.get(
  "milestone"
);

const State = {
  milestones: [
    {
      code: "M1",
      name: "browser.xhtml",
      title: "Strings loaded in browser.xhtml",
      categories: ["dtd", "ftl"],
      skipInDashboard: [],
      categoriesBar: [null, 1],
      columns: ["order", "type", "id"],
      columnSort: [0, "asc"],
    },
    {
      code: "M2",
      name: "startup",
      title: "Strings loaded during startup",
      categories: ["dtd", "properties", "ftl"],
      skipInDashboard: [],
      categoriesBar: [0, 2],
      columns: ["order", "type", "id", "stack"],
      columnSort: [0, "asc"],
    },
    {
      code: "M3",
      name: "mozilla-central",
      title: "Strings available in mozilla-central",
      categories: ["ini", "inc", "dtd", "properties", "ftl"],
      skipInDashboard: ["ini", "inc"],
      categoriesBar: [2, 4],
      columns: ["type", "file", "count"],
      columnSort: [5, "desc"],
    }
  ],
  currentMilestone: "M3",
  activeMilestone: activeMilestone || "M3"
};

const Page = {
  getActiveMilestone() {
    for (let milestone of State.milestones) {
      if (milestone.code == State.activeMilestone) {
        return milestone;
      }
    }
    for (let milestone of State.milestones) {
      if (milestone.code == State.currentMilestone) {
        return milestone;
      }
    }
    return null;
  },
};

async function loadFile() {
  let response = await fetch(`./data/${State.activeMilestone}/snapshot.json`);
  let snapshot = await response.json();

  document.getElementById("meta-milestone").textContent = State.activeMilestone;
  document.getElementById("meta-date").textContent = snapshot.date;
  document.getElementById("meta-rev").textContent = snapshot.revision;

  return prepareData(snapshot.data);
}

function formatStack(stack) {
  if (!stack) {
    return "";
  }
  if (typeof stack === "string") {
    return stack;
  }
  let title = "";
  for (let line of stack) {
    title += `[${line.index}] ${line.call} ${line.path}:${line.line}\n`;
  }
  let span = document.createElement("span");
  let path = stack[0].path.length > 70 ? "" : stack[0].path;
  span.textContent = `${stack[0].call} ${path}:${stack[0].line}`;
  span.setAttribute("title", title);
  return span.outerHTML;
}

function normalizePath(path) {
  let idx = path.indexOf("en-US/");
  if (idx === -1) {
    return path;
  }
  return path.substring(idx + 6);
}

function getEntryType(entry) {
  if (entry.type) {
    return entry.type;
  }
  return getTypeFromPath(entry.file);
}

function getEntryFile(entry) {
  if (entry.file) {
    return getLinkForPath(normalizePath(entry.file));
  }
  return "";
}

function getIdPath(entry) {
  if (entry.id) {
    return getLinkForId(entry.id);
  }
  return "";
}

const twoPartModules = [
  "devtools",
  "security",
];

function getLinkForPath(path) {
  let [mod] = path.split("/", 1);
  let moduleChunks = twoPartModules.includes(mod) ? 2 : 1;
  let module = path.split("/", moduleChunks).join("/");
  let rest = path.substr(module.length + 1);
  let sfPath = `https://searchfox.org/mozilla-central/source/${module}/locales/en-US/${rest}`;
  return `<a href="${sfPath}">${path}</a>`;
}

function getLinkForId(id) {
  let sfPath = `https://searchfox.org/mozilla-central/search?q=${id}&case=true`;
  return `<a href="${sfPath}">${id}</a>`;
}

function getTypeFromPath(path) {
  if (path.endsWith(".properties")) {
    return "properties";
  } else if (path.endsWith(".ftl")) {
    return "ftl";
  } else if (path.endsWith(".dtd")) {
    return "DTD";
  } else if (path.endsWith(".ini")) {
    return "ini";
  } else if (path.endsWith(".inc")) {
    return "inc";
  } else {
    throw new Error(`Unknown type for ${path}`);
  }
}

function prepareData(data) {
  let result = {
    data: [],
    columns: [],
    order: null
  };

  let i = 0;
  for (let entry of data) {
    result.data.push({
      order: entry.order || i,
      type: getEntryType(entry),
      file: getEntryFile(entry),
      stack: formatStack(entry.stack),
      count: entry.count || 1,
      id: getIdPath(entry),
    });
    i++;
  }

  let activeMilestone = Page.getActiveMilestone();
  result.columns = [
    { title: "Order", data: "order" , visible: activeMilestone.columns.includes("order")},
    { title: "Type", data: "type" , visible: activeMilestone.columns.includes("type")},
    { title: "ID", data: "id", visible: activeMilestone.columns.includes("id")},
    { title: "File", data: "file", visible: activeMilestone.columns.includes("file") },
    { title: "Stack", data: "stack", visible: activeMilestone.columns.includes("stack") },
    { title: "Count", data: "count", visible: activeMilestone.columns.includes("count") }
  ];
  result.order = activeMilestone.columnSort;
  return result;
}

$(document).ready(async function() {
  let { data, columns, order } = await loadFile();
  $("#example").DataTable({
    data,
    columns,
    order,
    pageLength: 25,
    destroy: true
  });
});
