'use strict';

var CHANNELS = ['R', 'G', 'B'];

// Returns a 6-digit uppercase hex string (no '#'), or null for empty input.
// Throws Error for anything that is not 3 or 6 hex digits.
function normalizeHex(input) {
    if (input === null || input === undefined) return null;
    var s = String(input).trim().replace(/^#/, '');
    if (s === '') return null;
    if (!/^[0-9a-fA-F]+$/.test(s)) {
        throw new Error('Invalid HEX color: use only 0-9 and A-F.');
    }
    if (s.length === 3) {
        s = s.split('').map(function (c) { return c + c; }).join('');
    }
    if (s.length !== 6) {
        throw new Error('Invalid HEX color: use 3 or 6 digits.');
    }
    return s.toUpperCase();
}

// Returns [r, g, b] or null for empty input. Throws on invalid input.
function hexToRgb(input) {
    var n = normalizeHex(input);
    if (n === null) return null;
    return [
        parseInt(n.slice(0, 2), 16),
        parseInt(n.slice(2, 4), 16),
        parseInt(n.slice(4, 6), 16)
    ];
}

// Full explanation object, or null for empty input.
function explain(input) {
    var n = normalizeHex(input);
    if (n === null) return null;
    var rgb = hexToRgb(n);
    var pairs = CHANNELS.map(function (ch, i) {
        return {
            channel: ch,
            pair: n.slice(i * 2, i * 2 + 2),
            value: rgb[i],
            percent: Math.round((rgb[i] / 255) * 10000) / 100
        };
    });
    return {
        hex: '#' + n,
        rgb: rgb,
        css: 'rgb(' + rgb.join(', ') + ')',
        pairs: pairs
    };
}

// Updates the page. `doc` is anything with getElementById (real or fake document).
function render(doc, input) {
    var err = doc.getElementById('error');
    var swatch = doc.getElementById('swatch');
    var summary = doc.getElementById('summary');
    var info = null;
    err.textContent = '';
    try {
        info = explain(input);
    } catch (e) {
        err.textContent = e.message;
    }
    if (!info) {
        swatch.style.background = '#222222';
        summary.textContent = err.textContent ? '' : 'Enter a hex color such as #1E90FF.';
        CHANNELS.forEach(function (ch) {
            doc.getElementById('bar' + ch).style.width = '0%';
            doc.getElementById('val' + ch).textContent = '-';
            doc.getElementById('pair' + ch).textContent = '-';
        });
        return null;
    }
    swatch.style.background = info.css;
    summary.textContent = info.hex + ' = ' + info.css;
    info.pairs.forEach(function (p) {
        doc.getElementById('bar' + p.channel).style.width = p.percent + '%';
        doc.getElementById('val' + p.channel).textContent = String(p.value);
        doc.getElementById('pair' + p.channel).textContent = p.pair + ' \u2192 ' + p.value;
    });
    return info;
}

if (typeof window !== 'undefined' && typeof document !== 'undefined') {
    window.addEventListener('load', function () {
        var inp = document.getElementById('hexInput');
        function update() { render(document, inp.value); }
        inp.addEventListener('input', update);
        update();
    });
}

if (typeof module !== 'undefined') {
    module.exports = { normalizeHex: normalizeHex, hexToRgb: hexToRgb, explain: explain, render: render };
}
