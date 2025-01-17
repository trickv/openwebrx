function Spectrum(el, msec) {
    this.el    = el;
    this.msec  = msec;
    this.ctx   = null;
    this.min   = 0;
    this.max   = 0;
    this.timer = 0;
    this.data  = [];

    // Make sure canvas fills the container
    el.style.width  = '100%';
    el.style.height = '100%';

    // Start with hidden spectrum display
    this.close();
}

Spectrum.prototype.update = function(data) {
    // Do not update if no redraw timer or no canvas
    if (!this.timer || (this.el.clientHeight == 0)) return;

    for(var j=0; j<data.length; ++j) {
        this.data[j] = j>=this.data.length || data[j]>this.data[j]?
            data[j] : this.data[j] + (data[j] - this.data[j]) / 10.0;
    }

//    this.min = Math.min(...data);
//    this.max = Math.max(...data);
    this.min = waterfall_min_level - 5;
    this.max = waterfall_max_level + 5;
};

Spectrum.prototype.draw = function() {
    // Do not draw if no redraw timer or no canvas
    if (!this.timer || (this.el.clientHeight == 0)) return;

    var vis_freq    = get_visible_freq_range();
    var vis_center  = vis_freq.center;
    var vis_start   = 0.5 - (center_freq - vis_freq.start) / bandwidth;
    var vis_end     = 0.5 - (center_freq - vis_freq.end) / bandwidth;

    var data_start  = Math.round(fft_size * vis_start);
    var data_end    = Math.round(fft_size * vis_end);
    var data_width  = data_end - data_start;
    var data_height = Math.abs(this.max - this.min);
    var spec_width  = this.el.offsetWidth;
    var spec_height = this.el.offsetHeight;

    // If canvas got resized, or no context yet...
    if (!this.ctx || spec_width!=this.el.width || spec_height!=this.el.height) {
        this.el.width  = spec_width;
        this.el.height = spec_height;
        this.ctx       = this.el.getContext("2d");
        this.ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
    }

    // Clear canvas to transparency
    this.ctx.clearRect(0, 0, spec_width, spec_height);

    if(spec_width <= data_width) {
        var x_ratio = data_width / spec_width;
        var y_ratio = spec_height / data_height;
        for(var x=0; x<spec_width; x++) {
            var y = (this.data[data_start + ((x * x_ratio) | 0)] - this.min) * y_ratio;
            this.ctx.fillRect(x, spec_height, 1, -y);
        }
    } else {
        var x_ratio = spec_width / data_width;
        var y_ratio = spec_height / data_height;
        var x_pos   = 0;
        for(var x=0; x<data_width; x++) {
            var y = (this.data[data_start + x] - this.min) * y_ratio;
            var k = ((x + 1) * x_ratio) | 0;
            this.ctx.fillRect(x_pos, spec_height, k - x_pos, -y);
            x_pos = k;
        }
    }
};

Spectrum.prototype.close = function() {
    // Hide container
    $('.openwebrx-spectrum-container').removeClass('expanded');

    // Stop redraw timer
    if (this.timer) {
        clearInterval(this.timer);
        this.timer = 0;
    }

    // Clear spectrum data
    this.data = [];
}

Spectrum.prototype.open = function() {
    // Show container
    $('.openwebrx-spectrum-container').addClass('expanded');

    // Start redraw timer
    if (!this.timer) {
        var me = this;
        this.timer = setInterval(function() { me.draw(); }, this.msec);
    }
}

Spectrum.prototype.toggle = function() {
    // Toggle based on the current redraw timer state
    if (this.timer) this.close(); else this.open();
};
