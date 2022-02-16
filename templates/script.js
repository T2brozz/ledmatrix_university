const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
let days = []

function timeToDecimal(t) {
    t = t.split(':');
    return Math.round(parseFloat(parseInt(t[0], 10) + parseInt(t[1], 10) / 60).toFixed(2) * 10) / 10;
}

function convertToHHMM(info) {
    let hrs = parseInt(Number(info));
    let min = Math.round((Number(info) - hrs) * 60);
    return hrs + ':' + min;
}

window.onload = function () {
    let brightnessSlider = new rSlider({
        target: '#brightness',
        values: {min: 0, max: 100},
        step: 1,
        range: false,
        tooltip: true,
        scale: false,
        labels: false,
        onChange: function (vals) {
            postNewBrightness(vals)
        }
    });
    for (i = 0; i < 7; i++) {
        days.push(new rSlider({
            target: '#' + dayNames[i],
            values: {min: 0, max: 2375},
            step: 25,
            range: true,
            tooltip: true,
            scale: false,
            labels: false,
            set: [0, 1]
        }))
    }

    getInitialBrightness().then(data => {
        brightnessSlider.setValues(data, data);
    })
    getInitialAuto().then(data => {
        for (var key in data.on) {
            let on = (Math.ceil(timeToDecimal(data.on[key]) / 0.25) * 0.25);
            let off = (Math.ceil(timeToDecimal(data.off[key]) / 0.25) * 0.25);
            console.log(on, off)
            let slider = days[dayNames.indexOf(key)];
            slider.setValues(on * 100, off * 100);
        }
    })
    getInitialText()
}

function applyAutoTimer() {
    let post = {
        "on": {},
        "off": {}
    }

    for (i = 0; i < 7; i++) {
        let on, off;
        [on, off] = days[i].getValue().split(',')
        on = convertToHHMM(Number(on) / 100)
        off = convertToHHMM(Number(off) / 100)
        post.on[dayNames[i]] = on
        post.off[dayNames[i]] = off
    }
    let r = new XMLHttpRequest()
    r.open("POST", 'autodisplay/');
    r.setRequestHeader("Content-Type", "application/json");
    r.send(JSON.stringify(post));
}

function postNewBrightness(val) {
    let r = new XMLHttpRequest()
    r.open("POST", 'brightness/set?new_brightness=' + val);
    r.send()
}

function applyText() {
    let l1 = document.getElementById("line1").value;
    let l2 = document.getElementById("line2").value;
    let l3 = document.getElementById("line3").value;
    let r = new XMLHttpRequest()
    r.open("POST", `text/?line1=${l1}&line2=${l2}&line3=${l3}`);
    r.send()
}

async function getInitialBrightness() {
    let response = await fetch("brightness/get");
    let data = await response.json();
    return Number(data.brightness);
}

async function getInitialAuto() {
    let response = await fetch("autodisplay/");
    return await response.json();
}

async function getInitialText() {
    let response = await fetch("text/");
    let data = await response.json();
    document.getElementById("line1").value = data.line1;
    document.getElementById("line2").value = data.line2
    document.getElementById("line3").value = data.line3
}