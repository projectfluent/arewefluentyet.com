main();

async function main() {
    create_chart(
        "#strings-chart > canvas",
        await prepare_data("./data/progress.json"));
}

    // Seaside
    // backgroundColor: "#f4f8ce",
    // backgroundColor: "#81d5b2",
    // backgroundColor: "#398ba6",

    // Steel
    // backgroundColor: "#fcec9b",
    // backgroundColor: "#84A3B2",
    // backgroundColor: "#517082",

async function prepare_data(url) {
    let response = await fetch(url);
    let snapshots = await response.json();

    let max = 0;
    let labels = [];
    let datasets = {
        ini: {
            label: "*.ini",
            backgroundColor: "#3d4b5e",
            borderColor: "#3d4b5e",
            pointBorderColor: "#222",
            pointRadius: 0,
            data: [],
        },
        inc: {
            label: "*.inc",
            backgroundColor: "#3d4b5e",
            borderColor: "#3d4b5e",
            pointBorderColor: "#222",
            pointRadius: 0,
            data: [],
        },
        dtd: {
            label: "DTD",
            backgroundColor: "#46698d",
            borderColor: "#46698d",
            pointBorderColor: "#222",
            data: [],
        },
        properties: {
            label: "Properties",
            backgroundColor: "#696890",
            borderColor: "#696890",
            pointBorderColor: "#222",
            data: [],
        },
        ftl: {
            label: "Fluent",
            backgroundColor: "#EB6896",
            borderColor: "#EB6896",
            pointBorderColor: "#222",
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
            },
        },
    });
}
