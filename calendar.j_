const canvas = document.getElementById("ganttChart");


// --------------------------------------------------
// Настраиваем высоту графика
// --------------------------------------------------

const chartHeight = works.length * 35 + 100;

const ganttWrapper = document.querySelector(".gantt-wrapper");

ganttWrapper.style.height = `${chartHeight}px`;


// --------------------------------------------------
// Названия работ
// --------------------------------------------------

const labels = works.map(work => work.name);


// --------------------------------------------------
// Данные графика
// --------------------------------------------------

const data = works.map(work => {

    return {
        x: [
            work.start,
            work.end
        ],
        y: work.name
    };

});


// --------------------------------------------------
// Цвета
// --------------------------------------------------

const colors = works.map(work => {

    if (work.type === "stage") {
        return "#7e7152";
    }

    return "#a0967e";

});


// --------------------------------------------------
// Создание графика
// --------------------------------------------------

new Chart(canvas, {

    type: "bar",

    data: {

        labels: labels,

        datasets: [

            {
                label: "Строительно-монтажные работы",

                data: data,

                backgroundColor: colors,

                borderColor: colors,

                borderWidth: 1,

                borderRadius: 0,

                barPercentage: 0.65,

                categoryPercentage: 0.8
            }

        ]

    },


    options: {

        indexAxis: "y",

        responsive: true,

        maintainAspectRatio: false,


        // ------------------------------------------
        // Взаимодействие
        // ------------------------------------------

        interaction: {

            mode: "nearest",

            axis: "y",

            intersect: false

        },


        // ------------------------------------------
        // Всплывающая подсказка
        // ------------------------------------------

        plugins: {

            legend: {

                display: false

            },


            tooltip: {

                callbacks: {

                    title: function(context) {

                        const index =
                            context[0].dataIndex;

                        return works[index].name;

                    },


                    label: function(context) {

                        const index =
                            context.dataIndex;

                        const work =
                            works[index];

                        return [
                            `Начало: ${work.start}`,
                            `Окончание: ${work.end}`
                        ];

                    }

                }

            }

        },


        // ------------------------------------------
        // Оси
        // ------------------------------------------

        scales: {

            x: {

                type: "time",

                min: "2025-04-01",

                max: "2026-12-31",


                time: {

                    unit: "month",

                    tooltipFormat: "dd.MM.yyyy",

                    displayFormats: {

                        month: "MMM yyyy"

                    }

                },


                title: {

                    display: true,

                    text: "Период реализации проекта",

                    font: {

                        size: 14

                    }

                },


                grid: {

                    color: "#D9D9D9",

                    lineWidth: 1

                }

            },


            y: {

                reverse: true,


                ticks: {

                    font: {

                        size: 11

                    }

                },


                grid: {

                    display: false

                }

            }

        }

    }

});