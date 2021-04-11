
/* Original code taken from https://github.com/cpsievert/LDAvis */
/* Copyright 2013, AT&T Intellectual Property */
/* MIT Licence */

'use strict';

var LDAvis = function(to_select, data_or_file_name) {

    // This section sets up the logic for event handling
    var current_clicked = {
        what: "nothing",
        element: undefined
    },
        current_hover = {
            what: "nothing",
            element: undefined
        },
        old_winning_state = {
            what: "nothing",
            element: undefined
        },
        vis_state = {
            lambda: 1,
            topic: 0,
            term: ""
        };

    // Set up a few 'global' variables to hold the data:
    var K, // number of topics
        R, // number of terms to display in bar chart
        mdsData, // (x,y) locations and topic proportions
        mdsData3, // topic proportions for all terms in the viz
        lamData, // all terms that are among the top-R most relevant for all topics, lambda values
        lambda = {
            old: 1,
            current: 1
        },
        color1 = "#1f77b4", // baseline color for default topic circles and overall term frequencies
        color2 = "#d62728"; // 'highlight' color for selected topics and term-topic frequencies

    // Set the duration of each half of the transition:
    var duration = 750;

    // Set global margins used for everything
    var margin = {
        top: 30,
        right: 30,
        bottom: 70,
        left: 30
    },
        mdswidth = 530,
        mdsheight = 530,
        barwidth = 530,
        barheight = 530,
        termwidth = 90, // width to add between two panels to display terms
        mdsarea = mdsheight * mdswidth;
    // controls how big the maximum circle can be
    // doesn't depend on data, only on mds width and height:
    var rMax = 60;

    // proportion of area of MDS plot to which the sum of default topic circle areas is set
    var circle_prop = 0.25;
    var word_prop = 0.25;

    // opacity of topic circles:
    var base_opacity = 0.2,
        highlight_opacity = 0.6;

    // topic/lambda selection names are specific to *this* vis
    var topic_select = to_select + "-topic";
    var lambda_select = to_select + "-lambda";

    // get rid of the # in the to_select (useful) for setting ID values
    var visID = to_select.replace("#", "");
    var topicID = visID + "-topic";
    var lambdaID = visID + "-lambda";
    var termID = visID + "-term";
    var topicDown = topicID + "-down";
    var topicUp = topicID + "-up";
    var topicClear = topicID + "-clear";

    var leftPanelID = visID + "-leftpanel";
    var barFreqsID = visID + "-bar-freqs";
    var topID = visID + "-top";
    var lambdaInputID = visID + "-lambdaInput";
    var lambdaZeroID = visID + "-lambdaZero";
    var sliderDivID = visID + "-sliderdiv";
    var lambdaLabelID = visID + "-lamlabel";

    //////////////////////////////////////////////////////////////////////////////

    // sort array according to a specified object key name
    // Note that default is decreasing sort, set decreasing = -1 for increasing
    // adpated from http://stackoverflow.com/questions/16648076/sort-array-on-key-value
    function fancysort(key_name, decreasing) {
        decreasing = (typeof decreasing === "undefined") ? 1 : decreasing;
        return function(a, b) {
            if (a[key_name] < b[key_name])
                return 1 * decreasing;
            if (a[key_name] > b[key_name])
                return -1 * decreasing;
            return 0;
        };
    }


    function visualize(data) {

        // set the number of topics to global variable K:
        K = data['mdsDat'].x.length;

        // R is the number of top relevant (or salient) words whose bars we display
        R = Math.min(data['R'], 30);

        // a (K x 5) matrix with columns x, y, topics, Freq, cluster (where x and y are locations for left panel)
        mdsData = [];
        for (var i = 0; i < K; i++) {
            var obj = {};
            for (var key in data['mdsDat']) {
                obj[key] = data['mdsDat'][key][i];
            }
            mdsData.push(obj);
        }

        // a huge matrix with 3 columns: Term, Topic, Freq, where Freq is all non-zero probabilities of topics given terms
        // for the terms that appear in the barcharts for this data
        mdsData3 = [];
        for (var i = 0; i < data['token.table'].Term.length; i++) {
            var obj = {};
            for (var key in data['token.table']) {
                obj[key] = data['token.table'][key][i];
            }
            mdsData3.push(obj);
        }

        // large data for the widths of bars in bar-charts. 6 columns: Term, logprob, loglift, Freq, Total, Category
        // Contains all possible terms for topics in (1, 2, ..., k) and lambda in the user-supplied grid of lambda values
        // which defaults to (0, 0.01, 0.02, ..., 0.99, 1).
        lamData = [];
        for (var i = 0; i < data['tinfo'].Term.length; i++) {
            var obj = {};
            for (var key in data['tinfo']) {
                obj[key] = data['tinfo'][key][i];
            }
            lamData.push(obj);
        }
        var dat3 = lamData.slice(0, R);

        // Create the topic input & lambda slider forms. Inspired from:
        // http://bl.ocks.org/d3noob/10632804
        // http://bl.ocks.org/d3noob/10633704
        init_forms(topicID, lambdaID, visID);

        // When the value of lambda changes, update the visualization
        console.log('lambda_select', lambda_select);
        d3.select(lambda_select)
            .on("mouseup", function() {
                console.log('lambda_select mouseup');
                // store the previous lambda value
                lambda.old = lambda.current;
                lambda.current = document.getElementById(lambdaID).value;
                vis_state.lambda = +this.value;
                // adjust the text on the range slider
                d3.select(lambda_select).property("value", vis_state.lambda);
                d3.select(lambda_select + "-value").text(vis_state.lambda);
                // transition the order of the bars
                var increased = lambda.old < vis_state.lambda;
                if (vis_state.topic > 0) reorder_bars(increased);
                // store the current lambda value
                state_save(true);
                document.getElementById(lambdaID).value = vis_state.lambda;
            });

        d3.select("#" + topicUp)
            .on("click", function() {
                // remove term selection if it exists (from a saved URL)
                var termElem = document.getElementById(termID + vis_state.term);
                if (termElem !== undefined) term_off(termElem);
                vis_state.term = "";
                var value_old = document.getElementById(topicID).value;
                var value_new = Math.min(K, +value_old + 1).toFixed(0);
                // increment the value in the input box
                document.getElementById(topicID).value = value_new;
                topic_off(document.getElementById(topicID + value_old));
                topic_on(document.getElementById(topicID + value_new));
                vis_state.topic = value_new;
                state_save(true);
            });

        d3.select("#" + topicDown)
            .on("click", function() {
                // remove term selection if it exists (from a saved URL)
                var termElem = document.getElementById(termID + vis_state.term);
                if (termElem !== undefined) term_off(termElem);
                vis_state.term = "";
                var value_old = document.getElementById(topicID).value;
                var value_new = Math.max(0, +value_old - 1).toFixed(0);
                // increment the value in the input box
                document.getElementById(topicID).value = value_new;
                topic_off(document.getElementById(topicID + value_old));
                topic_on(document.getElementById(topicID + value_new));
                vis_state.topic = value_new;
                state_save(true);
            });

        d3.select("#" + topicID)
            .on("keyup", function() {
                // remove term selection if it exists (from a saved URL)
                var termElem = document.getElementById(termID + vis_state.term);
                if (termElem !== undefined) term_off(termElem);
                vis_state.term = "";
                topic_off(document.getElementById(topicID + vis_state.topic));
                var value_new = document.getElementById(topicID).value;
                if (!isNaN(value_new) && value_new > 0) {
                    value_new = Math.min(K, Math.max(1, value_new));
                    topic_on(document.getElementById(topicID + value_new));
                    vis_state.topic = value_new;
                    state_save(true);
                    document.getElementById(topicID).value = vis_state.topic;
                }
            });

        d3.select("#" + topicClear)
            .on("click", function() {
                state_reset();
                state_save(true);
            });

        // create linear scaling to pixels (and add some padding on outer region of scatterplot)
        var xrange = d3.extent(mdsData, function(d) {
            return d.x;
        }); //d3.extent returns min and max of an array
        var xdiff = xrange[1] - xrange[0],
            xpad = 0.05;
        var yrange = d3.extent(mdsData, function(d) {
            return d.y;
        });
        var ydiff = yrange[1] - yrange[0],
            ypad = 0.05;

        if (xdiff > ydiff) {
            var xScale = d3.scale.linear()
                    .range([0, mdswidth])
                    .domain([xrange[0] - xpad * xdiff, xrange[1] + xpad * xdiff]);

            var yScale = d3.scale.linear()
                    .range([mdsheight, 0])
                    .domain([yrange[0] - 0.5*(xdiff - ydiff) - ypad*xdiff, yrange[1] + 0.5*(xdiff - ydiff) + ypad*xdiff]);
        } else {
            var xScale = d3.scale.linear()
                    .range([0, mdswidth])
                    .domain([xrange[0] - 0.5*(ydiff - xdiff) - xpad*ydiff, xrange[1] + 0.5*(ydiff - xdiff) + xpad*ydiff]);

            var yScale = d3.scale.linear()
                    .range([mdsheight, 0])
                    .domain([yrange[0] - ypad * ydiff, yrange[1] + ypad * ydiff]);
        }

        // Create new svg element (that will contain everything):
        var svg = d3.select(to_select).append("svg")
                .attr("width", mdswidth + barwidth + margin.left + termwidth + margin.right)
                .attr("height", mdsheight + 2 * margin.top + margin.bottom + 2 * rMax);

        // Create a group for the mds plot
        var mdsplot = svg.append("g")
                .attr("id", leftPanelID)
                .attr("class", "points")
                .attr("transform", "translate(" + margin.left + "," + 2 * margin.top + ")");

        // Clicking on the mdsplot should clear the selection
        mdsplot
            .append("rect")
            .attr("x", 0)
            .attr("y", 0)
            .attr("height", mdsheight)
            .attr("width", mdswidth)
            .style("fill", color1)
            .attr("opacity", 0)
            .on("click", function() {
                state_reset();
                state_save(true);
            });

        mdsplot.append("line") // draw x-axis
            .attr("x1", 0)
            .attr("x2", mdswidth)
            .attr("y1", mdsheight / 2)
            .attr("y2", mdsheight / 2)
            .attr("stroke", "gray")
            .attr("opacity", 0.3);
        mdsplot.append("text") // label x-axis
            .attr("x", 0)
            .attr("y", mdsheight/2 - 5)
            .text(data['plot.opts'].xlab)
            .attr("fill", "gray");

        mdsplot.append("line") // draw y-axis
            .attr("x1", mdswidth / 2)
            .attr("x2", mdswidth / 2)
            .attr("y1", 0)
            .attr("y2", mdsheight)
            .attr("stroke", "gray")
            .attr("opacity", 0.3);
        mdsplot.append("text") // label y-axis
            .attr("x", mdswidth/2 + 5)
            .attr("y", 7)
            .text(data['plot.opts'].ylab)
            .attr("fill", "gray");

        // new definitions based on fixing the sum of the areas of the default topic circles:
        var newSmall = Math.sqrt(0.02*mdsarea*circle_prop/Math.PI);
        var newMedium = Math.sqrt(0.05*mdsarea*circle_prop/Math.PI);
        var newLarge = Math.sqrt(0.10*mdsarea*circle_prop/Math.PI);
        var cx = 10 + newLarge,
            cx2 = cx + 1.5 * newLarge;

        // circle guide inspired from
        // http://www.nytimes.com/interactive/2012/02/13/us/politics/2013-budget-proposal-graphic.html?_r=0
        var circleGuide = function(rSize, size) {