/* ------------------------------------------------------------------------------
*
*  # Teal palette colors
*
*  Specific JS code additions for colors_teal.html page
*
*  Version: 1.0
*  Latest update: Aug 1, 2015
*
* ---------------------------------------------------------------------------- */

$(function() {


    // Selects
    // ------------------------------

    // Basic select2
    $('.select').select2({
        minimumResultsForSearch: "-1"
    });


    // Select2 ultiselect item color
    $('.select-item-color').select2({
        formatSelectionCssClass: function (data, container) { return "bg-teal"; }
    });


    // Select2 dropdown menu color
    $('.select-menu-color').select2({
        dropdownCssClass: 'bg-teal'
    });


    // Multiselect
    $('.multiselect').multiselect({
        buttonClass: 'btn bg-teal',
        nonSelectedText: 'Select your state',
        onChange: function() {
            $.uniform.update();
        }
    });


    // SelectBoxIt
    $(".selectbox").selectBoxIt({
        autoWidth: false,
        theme: "bootstrap"
    });


    // Bootstrap select
    $.fn.selectpicker.defaults = {
        iconBase: '',
        tickIcon: 'icon-checkmark-circle'
    };
    $('.bootstrap-select').selectpicker();



    // Notifications
    // ------------------------------

    // jGrowl
    $('.growl-launch').on('click', function () {
        $.jGrowl('I am a well highlighted teal notice..', { theme: 'bg-teal-400', header: 'Well highlighted' });
    });


    // PNotify
    $('.pnotify-launch').on('click', function () {
        new PNotify({
            title: 'teal Notice',
            text: 'Check me out! I\'m a notice.',
            icon: 'icon-teal22',
            animate_speed: 200,
            delay: 5000,
            addclass: 'bg-teal-400'
        });
    });



    // Form components
    // ------------------------------

    // Switchery toggle
    var switchery = document.querySelector('.switch');
    var init = new Switchery(switchery, {color: '#009688'});


    // Checkboxes and radios
    $(".styled, .multiselect-container input").uniform({
        radioClass: 'choice',
        checkboxClass: 'checker',
        wrapperClass: "border-teal text-teal-600"
    });


    // File input
    $(".file-styled").uniform({
        wrapperClass: 'bg-teal',
        fileButtonHtml: '<i class="icon-cloud-upload2"></i>'
    });



    // Popups
    // ------------------------------

    // Tooltip
    $('[data-popup=tooltip-custom]').tooltip({
        template: '<div class="tooltip"><div class="bg-teal"><div class="tooltip-arrow"></div><div class="tooltip-inner"></div></div></div>'
    });


    // Popover title
    $('[data-popup=popover-custom]').popover({
        template: '<div class="popover border-teal"><div class="arrow"></div><h3 class="popover-title bg-teal"></h3><div class="popover-content"></div></div>'
    });


    // Popover background color
    $('[data-popup=popover-solid]').popover({
        template: '<div class="popover bg-teal"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>'
    });

});
