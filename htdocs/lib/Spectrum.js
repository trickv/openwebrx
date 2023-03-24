function Spectrum(id) {
    this.el  = document.getElementById(id);
    this.ctx = this.el.getContext("2d");
}

Spectrum.prototype.draw = function(data) {
    var vis_freq    = get_visible_freq_range();
    var vis_center  = vis_freq.center;
    var vis_start   = 0.5 - (center_freq - vis_freq.start) / bandwidth;
    var vis_end     = 0.5 - (center_freq - vis_freq.end) / bandwidth;

    var data_start  = Math.round(fft_size * vis_start);
    var data_end    = Math.round(fft_size * vis_end);
    var data_width  = data_end - data_start;
    var data_height = Math.abs(waterfall_min_level - waterfall_max_level);
    var spec_width  = window.screen.width;
    var spec_height = 100;

    ctx.clearRect(0, 0, spec_width,spec_height);

    if(spec_width > data_width)
    {
        var x_ratio = data_width / spec_width;
        var y_ratio = spec_height / data_height;
        for(var x=0; x<spec_width; x++)
        {
            var y = data[data_start + j * x_ratio] * y_ratio;
            ctx.drawRect(x, 0, x+1, y);
        }
    }
    else
    {
        var x_ratio = spec_width / data_width;
        var y_ratio = spec_height / data_height;
        for(var x=0; x<data_width; x++)
        {
            var y = data[data_start + j] * y_ratio;
            ctx.drawRect(x * x_ratio, 0, (x+1) * x_ratio, y);
        }
    }
};
