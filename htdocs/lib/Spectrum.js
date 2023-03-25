function Spectrum(el) {
    this.el   = el;
    this.data = [];
    this.ctx  = this.el.getContext("2d");
    this.min  = 0;
    this.max  = 0;

    this.ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
}

Spectrum.prototype.update = function(data) {
    for(var j=0; j<data.length; ++j) {
        this.data[j] = j>=this.data.length || data[j]>this.data[j]?
            data[j] : this.data[j] + (data[j] - this.data[j]) / 10.0;
    }

//    this.min = Math.min(...data);
    this.min = waterfall_min_level;
    this.max = Math.max(...data);
};

Spectrum.prototype.draw = function() {
    if (this.el.clientHeight == 0) return;

    var vis_freq    = get_visible_freq_range();
    var vis_center  = vis_freq.center;
    var vis_start   = 0.5 - (center_freq - vis_freq.start) / bandwidth;
    var vis_end     = 0.5 - (center_freq - vis_freq.end) / bandwidth;

    var data_start  = Math.round(fft_size * vis_start);
    var data_end    = Math.round(fft_size * vis_end);
    var data_width  = data_end - data_start;
    var data_height = Math.abs(this.max - this.min);
    var spec_width  = this.el.clientWidth;
    var spec_height = this.el.clientHeight;

    this.ctx.clearRect(0, 0, spec_width, spec_height);

    if(spec_width < data_width) {
        var x_ratio = data_width / spec_width;
        var y_ratio = spec_height / data_height;
        for(var x=0; x<spec_width; x++) {
            var y = (this.data[data_start + ((x * x_ratio) | 0)] - this.min) * y_ratio;
            this.ctx.fillRect(x, spec_height, 1, -y);
        }
    } else {
        var x_ratio = spec_width / data_width;
        var y_ratio = spec_height / data_height;
        for(var x=0; x<data_width; x++) {
            var y = (this.data[data_start + x] - this.min) * y_ratio;
            this.ctx.fillRect(x * x_ratio, spec_height, x_ratio, -y);
        }
    }
};
