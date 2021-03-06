/* ------------------------------------------------------------------------------
*
*  # Multiple navbars
*
*  Specific JS code additions for multiple navbar pages
*
*  Version: 1.0
*  Latest update: Aug 1, 2015
*
* ---------------------------------------------------------------------------- */

$(function() {


    // We use Select2 for selects
    // ------------------------------

    // Single
    $('#single').select2({
        width: 180,
        minimumResultsForSearch: '-1',
        allowClear: true,
        dropdownCssClass: 'bg-slate-600'
    });


    // Multiple
    $('#multiple').select2({
        width: 180,
        minimumResultsForSearch: '-1',
        allowClear: true,
        dropdownCssClass: 'bg-slate-600'
    });



    // Operate multiple navbars
    // ------------------------------

    //
    // Single navbar
    //

    $('#single').on('change', function(){

        // Value of selected item
        var vals = $(this).val();


        // If one select is active, another one is disabled
        if ((vals == 'main_top') || (vals == 'main_bottom') || (vals == 'secondary_top')) {
            $("#multiple").select2("disable");
        }
        else {
            $("#multiple").select2("enable");
        }


        // Main top
        if (vals == 'main_top') {
            $('body').addClass('navbar-top');
            $('#navbar-main').addClass('navbar-fixed-top');
        }
        else {
            $('body').removeClass('navbar-top');
            $('#navbar-main').removeClass('navbar-fixed-top');
        }


        // Secondary top (with affix)
        if (vals == 'secondary_top') {

            // Add affix
            $('#navbar-second').addClass('navbar-affix-md');
            $('.navbar-affix-md').affix({
                offset: {
                    top: function() {
                        return (this.top = $('body').children('.navbar').outerHeight(true));
                    }
                }
            });

            // When affixed
            $('.navbar-affix-md').on('affixed.bs.affix', function() {
                $(this).next('.page-header').css('margin-top', $(this).outerHeight());
            });

            // When on top
            $('.navbar-affix-md').on('affixed-top.bs.affix', function() {
                $(this).next('.page-header').css('margin-top', '');
            });
        }
        else {
            $('#navbar-second').removeClass('navbar-affix-md');
            $(window).off('.affix');
            $('#navbar-second').removeData('bs.affix').removeClass('affix affix-top affix-bottom');
        }


        // Main bottom
        if (vals == 'main_bottom') {
            $('#navbar-main').addClass('navbar-fixed-bottom');
            $('body').addClass('navbar-bottom');
        }
        else {
            $('#navbar-main').removeClass('navbar-fixed-bottom');
            $('body').removeClass('navbar-bottom');
        }
    });


    //
    // Multiple navbars
    //

    $('#multiple').on('change', function(){

        // Value of selected items
        var vals = $(this).val();


        // If one select is active, another one is disabled
        if ((vals == 'multiple_top') || (vals == 'multiple_bottom')) {
            $("#single").select2("disable");
        }
        else {
            $("#single").select2("enable");
        }


        // Multiple top
        if (vals == 'multiple_top') {
            $('body').addClass('navbar-top-md-md');
            $('#navbar-main, #navbar-second').wrapAll('<div class="navbar-fixed-top" />');
            
        }
        else {
            $('body').removeClass('navbar-top-md-md');
            $('body').children('.navbar-fixed-top').children().unwrap();
        }


        // Multiple bottom
        if (vals == 'multiple_bottom') {
            $('body').addClass('navbar-bottom-md-md');
            $('#navbar-main, #navbar-second').wrapAll('<div class="navbar-fixed-bottom" />');
            
        }
        else {
            $('body').removeClass('navbar-bottom-md-md');
            $('body').children('.navbar-fixed-bottom').children().unwrap();
        }
    });

});
