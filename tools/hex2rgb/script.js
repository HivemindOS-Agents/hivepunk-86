function hexToRgb(hex) {
    if (!hex) return null;
    hex = hex.replace(/^#/, '');
    if (hex.length === 3) {
        hex = hex.split('').map(function (hexChar) {
            return hexChar + hexChar;
        }).join('');
    }
    if (hex.length !== 6) {
        throw new Error('Invalid HEX color.');
    }
    const num = parseInt(hex, 16);
    const r = (num >> 16) & 255;
    const g = (num >> 8) & 255;
    const b = num & 255;
    return [r, g, b];
}

if (typeof window !== 'undefined') {
    window.onload = function () {
        const inp = document.getElementById('hexInput');
        const out = document.getElementById('output');
        const btn = document.getElementById('convertBtn');
        btn.addEventListener('click', function () {
            try {
                const res = hexToRgb(inp.value.trim());
                if (res) {
                    out.textContent = 'RGB: ' + res.join(', ');
                } else {
                    out.textContent = 'Invalid input.';
                }
            } catch (e) {
                out.textContent = e.message;
            }
        });
    };
}

if (typeof module !== 'undefined') {
    module.exports = {hexToRgb};
}
