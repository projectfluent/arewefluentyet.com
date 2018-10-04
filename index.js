import COLORS from "./colors.js";

main();

async function main() {
    create_chart(
        "#strings-chart > canvas",
        await prepare_data("./data/progress.json"));
}

async function prepare_data(url) {
    let response = await fetch(url);
    let snapshots = await response.json();

    let max = 0;
    let labels = [];
    let datasets = {
        ini: {
            label: "*.ini",
            backgroundColor: COLORS.other,
            borderColor: COLORS.other,
            pointBorderColor: COLORS.point,
            pointRadius: 0,
            data: [],
        },
        inc: {
            label: "*.inc",
            backgroundColor: COLORS.other,
            borderColor: COLORS.other,
            pointBorderColor: COLORS.point,
            pointRadius: 0,
            data: [],
        },
        dtd: {
            label: "DTD",
            backgroundColor: COLORS.dtd,
            borderColor: COLORS.dtd,
            pointBorderColor: COLORS.point,
            data: [],
        },
        properties: {
            label: "Properties",
            backgroundColor: COLORS.properties,
            borderColor: COLORS.properties,
            pointBorderColor: COLORS.point,
            data: [],
        },
        ftl: {
            label: "Fluent",
            backgroundColor: COLORS.fluent,
            borderColor: COLORS.fluent,
            pointBorderColor: COLORS.point,
            data: [],
        },
    }

    let ext_re = /\.(\w+)$/;

    for (let {date, data} of snapshots) {
        let total = 0;
        let snapshot = {
            properties: 0,
            dtd: 0,
            ftl: 0,
            inc: 0,
            ini: 0,
        };

        for (let platform of data) {
            for (let [path, count] of Object.entries(platform)) {
                total += count;

                let match = ext_re.exec(path);
                if (match === null) {
                    continue;
                }
                let [_, extension] = match;
                snapshot[extension] += count;
            }
        }

        max = Math.max(max, total);
        labels.push(new Date(date));
        for (let [format, count] of Object.entries(snapshot)) {
            datasets[format].data.push(count);
        }

    }

    return {
        max,
        labels,
        datasets: [...Object.values(datasets)],
    };
}

function create_chart(selector, {max, ...data}) {
    let ctx = document.querySelector(selector).getContext("2d");
    return new Chart(ctx, {
        type: "line",
        data,
        options: {
            maintainAspectRatio: false,
            title: {
                display: true,
                position: "top",
                text: "Number of localizable strings in mozilla-central",
                fontStyle: "normal",
                fontSize: 16,
            },
            scales: {
                xAxes: [{
                    type: "time",
                    time: {
                        unit: "month"
                    },
                    gridLines: {
                        display: false,
                    },
                }],
                yAxes: [{
                    stacked: true,
                    ticks: {
                        min: 0,
                        max: Math.ceil(max / 1000) * 1000,
                    },
                    gridLines: {
                        display: false,
                    },
                }]
            },
            legend: {
                display: true,
                position: "bottom",
            },
            elements: {
                point: {
                    radius: 2,
                    hitRadius: 5,
                },
                line: {
                    tension: 0,
                    borderWidth: 0,
                }

            },
            tooltips: {
                mode: "index",
                position: "nearest",
                intersect: false,
                itemSort(a, b) {
                    // By default, labels are listed in reverse order relative
                    // to the order of the datasets. Reverse them again.
                    return b.datasetIndex - a.datasetIndex;
                }
            },
        },
    });
}
