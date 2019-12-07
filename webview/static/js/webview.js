// Match the timestamp format to what we do in the backend
var parseDate = d3.time.format("%m/%d/%Y %H:%M:%S %Z").parse, formatDate = d3.time.format("%m/%d/%Y %H:%M:%S %Z")

function changeSwitcheryState(el,value){
    // toggle notifications
    if($(el).is(':checked')!=value){
        $(el).trigger("click")
    }
}

function ajaxError(jqXHR, textStatus, errorThrown) {
    // hooked into each ajax request to display errors in the top bar
    element = $('#apistatus');
    element.html('API IS OFFLINE - ' + errorThrown);
    alertColor(element, 'bg-danger-400');
}

function ajaxSuccess() {
    // hooked into each ajax request to show the api is still alive
    element = $('#apistatus');
    element.html('API IS ONLINE');
    alertColor(element, 'bg-success-400');
}

function alertColor(element, color) {
    // Toggle colors on widget 
    if (!element.hasClass(color)) {
        if (element.hasClass('bg-danger-400')) {
            element.removeClass('bg-danger-400', 1000);
        } else if (element.hasClass('bg-orange-400')) {
            element.removeClass('bg-orange-400', 1000);
        } else if (element.hasClass('bg-green-400')) {
            element.removeClass('bg-green-400', 1000);
        } else if (element.hasClass('bg-teal-400')) {
            element.removeClass('bg-teal-400', 1000);
        } else if (element.hasClass('bg-success-400')) {
            element.removeClass('bg-success-400', 1000);
        }
        element.addClass(color, 2000);
    }
}

function strTObool (str) {
    // work around not having data types in json and html
    if (str == "1") {
        return true;
    } else if (str == "0") {
        return false;
    } else if (str == "on") {
        return true;
    } else if (str == "off") {
        return false;
    } else {
        return null;
    }
}

function booltostr(bool) {
    // work around not having data types in json and html
    if (bool) {
        return 'Yes';
    } else if (!bool) {
        return 'No';
    } else {
        return null;
    }
}

// Used to update the snmp int widget
function updateSNMPint(host, check, unit) {
    $.ajax({
        url: '/data/' + host + '/' + check + '/int/' ,
        success: function(data) {
            $('#m4-' + host + '-' + check).html(parseFloat(data.data).toFixed(2) + ' ' + unit);
            element = $('#m4-' + host + '-' + check + '-content .panel')
            if (data.alert == 'crit') {
                alertColor(element, 'bg-danger-400');
            } else if (data.alert == 'warn') {
                alertColor(element, 'bg-orange-400');
            } else if (data.alert == 'ok') {
                alertColor(element, 'bg-green-400');
            } else if (data.alert == 'false') {
                alertColor(element, 'bg-teal-400');
            }
            // update the notification toggel from the new data in case it was toggled by someone else
            if (data.notifs == "true") {
                changeSwitcheryState(document.getElementById('m4-' + host + '--' + check + '-notifs'), true);
            } else {
                changeSwitcheryState(document.getElementById('m4-' + host + '--' + check + '-notifs'), false);
            }
            ajaxSuccess();
        },
        complete: this.ajax_complete,
        error: ajaxError,
        dataType: 'json'
    });
}

// Used to update the snmp BOOL widget
function updateSNMPbool(host, check) {
    $.ajax({
        url: '/data/' + host + '/' + check + '/bool/',
        success: function(data) {
            $('#m4-' + host + '-' + check).html(booltostr(strTObool(data.data)));
            element = $('#m4-' + host + '-' + check + '-content .panel')
            if (data.alert == 'crit') {
                alertColor(element, 'bg-danger-400');
            } else if (data.alert == 'ok') {
                alertColor(element, 'bg-green-400');
            } else if (data.alert == 'false') {
                alertColor(element, 'bg-teal-400');
            }
            // update the notification toggel from the new data in case it was toggled by someone else
            if (data.notifs == "true") {
                changeSwitcheryState(document.getElementById('m4-' + host + '--' + check + '-notifs'), true);
            } else {
                changeSwitcheryState(document.getElementById('m4-' + host + '--' + check + '-notifs'), false);
            }
            ajaxSuccess();
        },
        complete: this.ajax_complete,
        error: ajaxError,
        dataType: 'json'
    });
}

// Used to update the STR widget
function updateSNMPstr(host, check) {
    $.ajax({
        url: '/data/' + host + '/' + check + '/str/',
        success: function(data) {
            $('#m4-' + host + '-' + check).html(data.data);
            element = $('#m4-' + host + '-' + check + '-content .panel')
            if (data.alert == 'crit') {
                alertColor(element, 'bg-danger-400');
            } else if (data.alert == 'ok') {
                alertColor(element, 'bg-green-400');
            } else if (data.alert == 'warn') {
                alertColor(element, 'bg-orange-400');
            } else if (data.alert == 'false') {
                alertColor(element, 'bg-teal-400');
            }
            // update the notification toggel from the new data in case it was toggled by someone else
            if (data.notifs == "true") {
                changeSwitcheryState(document.getElementById('m4-' + host + '--' + check + '-notifs'), true);
            } else {
                changeSwitcheryState(document.getElementById('m4-' + host + '--' + check + '-notifs'), false);
            }
            ajaxSuccess();
        },
        complete: this.ajax_complete,
        error: ajaxError,
        dataType: 'json'
    });
}

// Used to update the event log
function updateEvents(qty) {
    $.ajax({
        url: '/eventlog/' + qty + '/',
        success: function(data) {
            $('#eventlog-body').html(data);
            ajaxSuccess();
        },
        complete: this.ajax_complete,
        error: ajaxError,
    });
}

// Used to update the sla
function updateSla() {
    $.ajax({
        url: '/sla/',
        success: function(data) {
            $('#sla-body').html(data);
            ajaxSuccess();
        },
        complete: this.ajax_complete,
        error: ajaxError,
    });
}

function updateTraps() {
    $.ajax({
        url: '/trap/',
        success: function(data) {
            $('#trap-body').html(data);
            ajaxSuccess();
        },
        complete: this.ajax_complete,
        error: ajaxError,
    });
}

// Used to update the sla log
function updateSlaLog(qty) {
    $.ajax({
        url: '/slalog/' + qty + '/',
        success: function(data) {
            $('#slalog-body').html(data);
            ajaxSuccess();
        },
        complete: this.ajax_complete,
        error: ajaxError,
    });
}

// Used to update the taskdelay
function updateTaskDelay(qty) {
    $.ajax({
        url: '/delay/' + qty + '/',
        success: function(data) {
            value = parseFloat(data)
            $('#taskdelay').html("Avg Task delay: " + value.toFixed(5) + " seconds");
            ajaxSuccess();
            if (value > 5) {
                alertColor($('#taskdelay'), 'bg-danger-400');
            } else if (value < 1) {
                alertColor($('#taskdelay'), 'bg-green-400');
            } else if (value > 1 ) {
                alertColor($('#taskdelay'), 'bg-orange-400');
            }
        },
        complete: this.ajax_complete,
        error: ajaxError,
    });
}

// Graph setup
function sparkline(element, chartType, qty, height, interpolation, duration, interval, color, graphdata, host, check, unit, verbosename, checktype) {

    // Basic setup
    // ------------------------------

    // Define main variables
    var d3Container = d3.select(element),
        margin = {top: 0, right: 0, bottom: 0, left: 0},
        width = d3Container[0][0].getBoundingClientRect().width - margin.left - margin.right,
        // width = 900,
        height = height - margin.top - margin.bottom;
    // console.log(d3Container[0][0].getBoundingClientRect());
    // console.log(d3Container[0].getBoundingClientRect());
    // console.log(d3Container.getBoundingClientRect());
    // console.log(d3Container.node().getBoundingClientRect().width);
    // Load data
    // ------------------------------        
    dataset = graphdata
    dataset.forEach(function (d) {
        d.datetime = parseDate(d.datetime);
    });

    // Construct scales
    // ------------------------------
    var padding = 0;

    // Horizontal
    var x = d3.time.scale().range([padding, width - padding]);

    // Vertical
    var y = d3.scale.linear().range([height, 5]);

    // Set input domains
    // ------------------------------

    if (checktype == 'int') {
        // Horizontal
        x.domain(d3.extent(dataset, function (d) {
            return d.datetime;
        }));

        // Vertical
        y.domain(d3.extent(dataset, function (d) {
            return d.value;
        }));        
    } else if (checktype == 'bool') {
        // Horizontal
        x.domain(d3.extent(dataset, function (d) {
            return d.datetime;
        }));

        // Vertical
        y.domain([0, 3]);        
    }

    // Construct chart layout
    // ------------------------------

    // Line
    var line = d3.svg.line()
        // .interpolate(interpolation)
        .x(function(d, i) { return x(d.datetime); })
        .y(function(d, i) { return y(d.value); });

    // Area
    var area = d3.svg.area()
        // .interpolate(interpolation)
        .x(function(d,i) { 
            return x(d.datetime); 
        })
        .y0(height)
        .y1(function(d) { 
            return y(d.value); 
        });

    if (checktype == 'int') {
        var tooltip = d3.tip()
            .attr('class', 'd3-tip')
            .html(function (d) {
                return "<ul class='list-unstyled mb-5'>" +
                    "<li>" + "<div class='text-size-base mt-5 mb-5'><i class='icon-check2 position-left'></i>" + formatDate(d.datetime) + "</div>" + "</li>" +
                    "<li>" + host.toUpperCase() + " " + verbosename + ": " + "<span class='text-semibold pull-right'>" + d.value + " " + unit + "</span>" + "</li>" + 
                    "<li>" + "Average " + verbosename + ": &nbsp; " + "<span class='text-semibold pull-right'>" + parseFloat(d.avg).toFixed(2) + " " + unit + "</span>" + "</li>" + 
                    "<li>" + "Min " + verbosename + ": &nbsp; " + "<span class='text-semibold pull-right'>" + parseFloat(d.min).toFixed(2) + " " + unit + "</span>" + "</li>" + 
                    "<li>" + "Max " + verbosename + ": &nbsp; " + "<span class='text-semibold pull-right'>" + parseFloat(d.max).toFixed(2) + " " + unit + "</span>" + "</li>" + 
                "</ul>";
            });
    } else if (checktype == 'bool') {
        var tooltip = d3.tip()
            .attr('class', 'd3-tip')
            .html(function (d) {
                return "<ul class='list-unstyled mb-5'>" +
                    "<li>" + "<div class='text-size-base mt-5 mb-5'><i class='icon-check2 position-left'></i>" + formatDate(d.datetime) + "</div>" + "</li>" +
                    "<li>" + host.toUpperCase() + " " + verbosename + ": " + "<span class='text-semibold pull-right'>" + booltostr(strTObool(d.value)) + "</span>" + "</li>" + 
                    "<li>" + "# of True " + verbosename + ": &nbsp; " + "<span class='text-semibold pull-right'>" + d.nbtrue + "</span>" + "</li>" + 
                    "<li>" + "# of False " + verbosename + ": &nbsp; " + "<span class='text-semibold pull-right'>" + d.nbfalse + "</span>" + "</li>" + 
                    "<li>" + "Last True " + verbosename + ": &nbsp; " + "<span class='text-semibold pull-right'>" + d.lasttrue + "</span>" + "</li>" + 
                    "<li>" + "Last False " + verbosename + ": &nbsp; " + "<span class='text-semibold pull-right'>" + d.lastfalse + "</span>" + "</li>" + 
                "</ul>";
            });
    }
    // Create SVG
    // ------------------------------

    // Container
    var container = d3Container.append('svg');

    // SVG element
    var svg = container
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")").call(tooltip);

    // Add mask for animation
    // ------------------------------

    // Add clip path
    var clip = svg.append("defs")
        .append("clipPath")
        .attr('id', function(d, i) { return "load-clip-" + element.substring(1) })

    // Add clip shape
    var clips = clip.append("rect")
        .attr('class', 'load-clip')
        .attr("width", 0)
        .attr("height", height);

    // Animate mask
    clips
        .transition()
            .duration(1000)
            .ease('linear')
            .attr("width", width);

    // Append chart elements
    // Main path
    var path = svg.append("g")
        .attr("clip-path", function(d, i) { return "url(#load-clip-" + element.substring(1) + ")"})
        .append("path")
        .data([dataset])
        .attr("transform", "translate(" + x(d3.min(dataset, function (d) { return d.datetime;})) + ",0)");

    // Add path based on chart type
    if(chartType == "area") {
        path.attr("d", area).attr('class', 'd3-area').style("fill", color); // area
    }
    else {
        path.attr("d", line).attr("class", "d3-line d3-line-medium").style('stroke', color); // line
    }

    // Animate path
    path
        .style('opacity', 0)
        .transition()
        .duration(750)
        .style('opacity', 1);

    // Add vertical guide lines
    // Bind data
    var guide = svg.append('g')
        .selectAll('.d3-line-guides-group')
        .data(dataset);

    // Append lines
    guide
        .enter()
        .append('line')
        .attr('class', 'd3-line-guides')
        .attr('x1', function (d, i) {
          // alert(d);
            return x(d.datetime);
        })
        .attr('y1', function (d, i) {
            return height;
        })
        .attr('x2', function (d, i) {
            return x(d.datetime);
        })
        .attr('y2', function (d, i) {
          // alert(y(d.alpha));
            return height;
        })
        .style('stroke', 'rgba(255,255,255,0.3)')
        .style('stroke-dasharray', '4,2')
        .style('shape-rendering', 'crispEdges');

    // Animate guide lines
    guide
        .transition()
        .duration(1000)
        .delay(function(d, i) { return i * 150; })
        .attr('y2', function (d, i) {
            return y(d.value);
        });

    // Alpha app points
    // ------------------------------

    // Add points
    var points = svg.insert('g')
        .selectAll('.d3-line-circle')
        .data(dataset)
        .enter()
        .append('circle')
        .attr('class', 'd3-line-circle d3-line-circle-medium')
        .attr("cx", line.x())
        .attr("cy", line.y())
        .attr("r", 3)
        .style('stroke', '#fff')
        .style('fill', '#26a69a');

    // Animate points on page load
    points
        .style('opacity', 0)
        .transition()
        .duration(250)
        .ease('linear')
        .delay(2000)
        .style('opacity', 1);

    // Add user interaction
    points
        .on("mouseover", function (d) {
            tooltip.offset([-10, 0]).show(d);
            // Animate circle radius
            d3.select(this).transition().duration(250).attr('r', 4);
        })

        // Hide tooltip
        .on("mouseout", function (d) {
            tooltip.hide(d);
            // Animate circle radius
            d3.select(this).transition().duration(250).attr('r', 3);
        });

    // Change tooltip direction of first point
    d3.select(points[0][0])
        .on("mouseover", function (d) {
            tooltip.offset([-10, 10]).direction('nw').show(d);
            // Animate circle radius
            d3.select(this).transition().duration(250).attr('r', 4);
        })
        .on("mouseout", function (d) {
            tooltip.direction('n').hide(d);
            // Animate circle radius
            d3.select(this).transition().duration(250).attr('r', 3);
        });

    // Change tooltip direction of last point
    d3.select(points[0][points.size() - 1])
        .on("mouseover", function (d) {
            tooltip.offset([-10, -10]).direction('ne').show(d);
            // Animate circle radius
            d3.select(this).transition().duration(250).attr('r', 4);
        })
        .on("mouseout", function (d) {
            tooltip.direction('n').hide(d);
            // Animate circle radius
            d3.select(this).transition().duration(250).attr('r', 3);
        })
}

$(function() { 
    // Switchery toggles
    // ------------------------------

    $(".modal").on("shown.bs.modal", function () { 
        setTimeout(function(){}, 500);
    });

    var switches = Array.prototype.slice.call(document.querySelectorAll('.switch'));
    switches.forEach(function(html) {
        var switchery = new Switchery(html, {color: '#4CAF50'});
    });

    var changeCheckboxes = Array.prototype.slice.call(document.querySelectorAll('.switch'));
    // console.log(changeCheckbox)
    changeCheckboxes.forEach(function(el) {
        if (el) {
            // console.log('Apply switchery to ' + el.id);
            el.onchange = function() {
                // console.log(el.name + " has changed to " + el.checked);
                $.ajax({
                    url: '/notifications/' + el.name + '/' + el.checked + '/',
                    success: function(data) {
                        console.log(data);
                        ajaxSuccess();
                    },
                    error: ajaxError,
                    dataType: 'html'
                });
            };
        } else {
            console.log('was null ' + el)
        };        
    });

    // resets modal windows
    $('body').on('hidden.bs.modal', '.modal', function () {
        $(this).removeData('bs.modal');
    });

    // action to refresh the notification drop down
    $( "#syncmsg" ).click(function() {
        $.ajax({
            url: '/msg/',
            success: function(data) {
                $('#msg').html(data);
                // update the count of notifications
                $('#msgcount').html($('#msg li').size());
                console.log();
                ajaxSuccess();
            },
            error: ajaxError,
            dataType: 'html'
        });
    });
});