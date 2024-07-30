const jQualifier1Data = {
    teams: [
        ["Jan Malek", "Tymur Keleberda"],
        ["Pranav Venkatesh", "Pranav Anand"],
        ["Ryo Chen", "Anthony Atanasov"],
        ["Balaji Daggupati", "Read Samadov"]
    ],
    results: [
        [
            [[1, 0], [1, 0], [1, 0], [1, 0]],
            [[1, 4], [2, 4]],
            [[4, 0]]
        ],
        [
            [[0.5, 3.5], [2.5, 3.5]],
            [[3.5, 2.5], [3.5, 1.5]],
            [[1, 4]],
            [[4, 3]]
        ]
    ]
};


const jQualifier2Data = {
    teams: [
        ["Daniel Dardha", "Harsh Suresh"],
        ["Sv. Bazakutsa", "Kaivalya Nagare"],
        ["Pranesh M", "Aditya Mittal"],
        ["Emin Ohanyan", "Jan Malek"]
    ],
    results: [
        [
            [[1, 0], [1, 0], [1, 0], [1, 0]],
            [[0.5, 3.5], [2.5, 3.5]],
            [[0.5, 3.5]]
        ],
        [
            [[4, 3.5], [4, 2]],
            [[3.5, 1.5], [1.5, 3.5]],
            [[0.5, 3.5]],
            [[3.5, 0.5]]
        ]
    ]
};

$(function () {
    $('#junior_qualifier1').bracket({
        init: jQualifier1Data,
        skipConsolationRound: true,
        teamWidth: 120,
        scoreWidth: 25,
        matchMargin: 25,
        roundMargin: 10
    });
});

$(function () {
    $('#junior_qualifier2').bracket({
        init: jQualifier2Data,
        skipConsolationRound: true,
        dir: 'rl',
        teamWidth: 120,
        scoreWidth: 25,
        matchMargin: 25,
        roundMargin: 10
    });
});

const jMainData = {
    teams: [
        ["Dommaraju Gukesh", "Emin Ohanyan"],
        ["Christopher Woojin Yoo", "Pranav Venkatesh"],
        ["Raunak Sadhwani", "Read Samadov"],
        ["Denis V. Lazavik", "Daniel Dardha"]
    ],
    results: [
        [
            [[25, 6], [11.5, 12.5], [20.5, 6.5], [19, 5]],
            [[16.5, 10.5], [15.5, 10.5]],
            [[17.5, 10.5]]
        ]
    ]
};

$(function () {
    $('#juniorMain').bracket({
        init: jMainData,
        skipConsolationRound: true,
        teamWidth: 160,
        scoreWidth: 35,
        matchMargin: 25,
        roundMargin: 15
    });
});

const bQualifier1Data = {
    teams: [
        ["Yoseph T. Taher", "Denis Lazavik"],
        ["Emin Ohanyan", "Matthias Blübaum"],
        ["Aydın Süleymanlı", "Dmitry Andreikin"],
        ["José Martínez", "Renato Terry"]
    ],
    results: [
        [
            [[1, 0], [1, 0], [1, 0], [1, 0]],
            [[4, 5], [3, 5]],
            [[1.5, 6.5]]
        ],
        [
            [[8, 2], [2.5, 5.5]],
            [[4, 5], [6, 3]],
            [[4.5, 5.5]],
            [[3.5, 4.5]]
        ]
    ]
};

const bQualifier2Data = {
    teams: [
        ["David Paravyan", "Luca Moroni"],
        ["Sasha Grischuk", "Rauf Mamedov"],
        ["Denis Lazavik", "Vl. Zakhartsov"],
        ["Renato Terry", "Sergei Zhigalko"]
    ],
    results: [
        [
            [[1, 0], [1, 0], [1, 0], [1, 0]],
            [[7, 4], [5, 3]],
            [[7, 3]]
        ],
        [
            [[3.5, 5.5], [2.5, 7.5]],
            [[4, 5], [6, 5]],
            [[5.5, 2.5]],
            [[3, 7]]
        ]
    ]
};

const bQualifier3Data = {
    teams: [
        ["Dmitry Andreikin", "Renato Terry"],
        ["S. L. Narayanan", "Sasha Grischuk"],
        ["Arjun Erigaisi", "Cristóbal Villagra"],
        ["Federico Perez", "Rauf Mamedov"]
    ],
    results: [
        [
            [[1, 0], [1, 0], [1, 0], [1, 0]],
            [[5.5, 3.5], [5.5, 2.5]],
            [[5.5, 4.5]]
        ],
        [
            [[3.5, 4.5], [3, 7]],
            [[7, 2], [6, 4]],
            [[5, 7]],
            [[1.5, 5.5]]
        ]
    ]
};

$(function () {
    $('#bullet_qualifier1').bracket({
        init: bQualifier1Data,
        skipConsolationRound: true,
        teamWidth: 120,
        scoreWidth: 25,
        matchMargin: 25,
        roundMargin: 10
    });
});

$(function () {
    $('#bullet_qualifier2').bracket({
        init: bQualifier2Data,
        skipConsolationRound: true,
        dir: 'rl',
        teamWidth: 120,
        scoreWidth: 25,
        matchMargin: 25,
        roundMargin: 10
    });
});

$(function () {
    $('#bullet_qualifier3').bracket({
        init: bQualifier3Data,
        skipConsolationRound: true,
        teamWidth: 120,
        scoreWidth: 25,
        matchMargin: 25,
        roundMargin: 10
    });
});

const bMainData = {
    teams: [
        ["Hikaru Nakamura", "Emin Ohanyan"],
        ["Anish Giri", "José Martínez Alcántara"],
        ["Daniel Naroditsky", "David Paravyan"],
        ["Andrew Tang", "Dmitry Andreikin"],
        ["Magnus Carlsen", "Eric Hansen"],
        ["Lê Tuấn Minh", "Arjun Erigaisi"],
        ["Alireza Firouzja", "Denis Lazavik"],
        ["Oleksandr Bortnyk", "Fabiano Caruana"]
    ],
    results: [
        [
            [[22.5, 1.5], [11.5, 12.5], [11.5, 5.5], [12.5, 3.5], [16.5, 1.5], [11, 6], [14.5, 3.5], [14, 5]],
            [[14, 6], [14.5, 6.5], [10, 7], [11, 5]],
            [[20, 12], [11.5, 14.5]],
            [[16.5, 12.5]]
        ],
        [
            [[8.5, 6.5], [11.5, 7.5], [1, 0], [11.5, 9.5]],
            [[0, 1], [9, 7], [3, 14], [7, 9]],
            [[9, 7], [10, 7]],
            [[6, 13], [7.5, 13.5]],
            [[7.5, 12.5]],
            [[11, 9]]
        ],
        [
            [[17, 15]]
        ]
    ]
};

$(function () {
    $('#bulletMain').bracket({
        init: bMainData,
        skipConsolationRound: true,
        teamWidth: 160,
        scoreWidth: 35,
        matchMargin: 25,
        roundMargin: 15
    });
});

const qualifier1Data = {
    teams: [
        ["Yu Yangyi", "Matthias Blübaum"],
        ["Rodrigo Vásquez", "Denis Lazavik"],
        ["Rauf Mamedov", "Aram Hakobyan"],
        ["Bogdan Deac", "Vidit S. Gujrathi"]
    ],
    results: [
        [
            [[1, 0], [1, 0], [1, 0], [1, 0]],
            [[4, 3], [2, 4]],
            [[4, 3]]
        ],
        [
            [[1, 4], [2, 4]],
            [[2.5, 3.5], [3, 1]],
            [[1.5, 3.5]],
            [[4, 3]]
        ]
    ]
};

const qualifier2Data = {
    teams: [
        ["Alexey Sarana", "Aram Hakobyan"],
        ["Eduardo Iturrizaga", "David Paravyan"],
        ["Dmitry Andreikin", "Raunak Sadhwani"],
        ["Alex Shimanov", "Kirill Shevchenko"]
    ],
    results: [
        [
            [[1, 0], [1, 0], [1, 0], [1, 0]],
            [[3.5, 2.5], [3.5, 1.5]],
            [[4, 1]]
        ],
        [
            [[3.5, 1.5], [4, 3]],
            [[3.5, 0.5], [1.5, 3.5]],
            [[1.5, 3.5]],
            [[0.5, 3.5]]
        ]
    ]
};

$(function () {
    $('#qualifier1').bracket({
        init: qualifier1Data,
        skipConsolationRound: true,
        teamWidth: 120,
        scoreWidth: 25,
        matchMargin: 25,
        roundMargin: 10
    });
});

$(function () {
    $('#qualifier2').bracket({
        init: qualifier2Data,
        skipConsolationRound: true,
        dir: 'rl',
        teamWidth: 120,
        scoreWidth: 25,
        matchMargin: 25,
        roundMargin: 10
    });
});

const mainData = {
    teams: [
        ["Hikaru Nakamura", "Yu Yangyi"],
        ["Fabiano Caruana", "Nodirbek Abdusattorov"],
        ["Nihal Sarin", "Alexey Sarana"],
        ["Maxime Vachier-Lagrave", "Dommaraju Gukesh"],
        ["Magnus Carlsen", "Vidit Santosh Gujrathi"],
        ["Ian Nepomniachtchi", "Arjun Erigaisi"],
        ["Alireza Firouzja", "Dmitry Andreikin"],
        ["Wesley So", "Levon Aronian"]
    ],
    results: [
        [
            [[19, 9], [13.5, 10.5], [16, 10], [21.5, 8.5], [17.5, 8.5], [15.5, 14.5], [13.5, 12.5], [15.5, 12.5]],
            [[18.5, 8.5], [11.5, 19.5], [20.5, 9.5], [15.5, 16.5]],
            [[16.5, 11.5], [22, 7]],
            [[12.5, 13.5]]
        ]
    ]
};

width = $(window).width();

$(function () {
    const tW = 7 / 96;
    const sW = 3 / 160;
    const mM = 7 / 640;
    const rM = 7 / 960;
    $('#main').bracket({
        init: mainData,
        skipConsolationRound: true,
        teamWidth: width * tW,
        scoreWidth: width * sW,
        matchMargin: width * mM,
        roundMargin: width * rM
    });
    $('#mainBracket').css({
        'width': width * 4 * (tW + sW + rM) + 'px',
    });
});