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
        ftl: {
            label: "Fluent",
            backgroundColor: "#EB6896",
            borderColor: "#EB6896",
            data: [],
        },
        dtd: {
            label: "DTD",
            backgroundColor: "#696890",
            borderColor: "#696890",
            data: [],
        },
        properties: {
            label: "Properties",
            backgroundColor: "#46698d",
            borderColor: "#46698d",
            data: [],
        },
        ini: {
            label: "*.ini",
            backgroundColor: "#666",
            borderColor: "#666",
            data: [],
        },
        inc: {
            label: "*.inc",
            backgroundColor: "#666",
            borderColor: "#666",
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
                    }
                }],
                yAxes: [{
                    stacked: true,
                    ticks: {
                        min: 0,
                        max: Math.ceil(max / 1000) * 1000,
                    },
                }]
            },
            legend: {
                display: true,
                position: "bottom",
            },
            elements: {
                point: {
                    radius: 0,
                },
                line: {
                    tension: 0,
                    borderWidth: 0,
                }

            },
            hover: {
                mode: "index",
            }
        },
    });
}
