/* jshint esnext: true */
var jQuery, document, window, location, swal;
(function ($) {
    "use strict";

    const dh = {
        dev: 'CrazyDH',
        flex_center: 'flex_center',
        popupVdo: $('.eco--popup')
    };

    dh.subMenu = $('.sub-menu');
    if (dh.subMenu.length) {
        dh.subMenu.each(function () {
            $(this).closest('li').addClass('has-dropdown');
        });
    }

    // preloader
    dh.fnPreloader = () => {
        dh.preloader = $('.preloader');
        if (dh.preloader.length) {
            dh.preloader.fadeOut(1000);
        }
    };


    // height configuration

    dh.heightConfig = () => {
        dh.autoHeight = customClass => {
            let minHeight = -1;
            customClass.each(function () {
                if ($(this).height() > minHeight) {
                    minHeight = $(this).height();
                }
            });
            customClass.height(minHeight).addClass(dh.flex_center);
        };
        dh.home_height1 = $('.eco--home--height--1');
        dh.autoHeight(dh.home_height1);

        dh.sPricing1Li = $('.eco--single--pricing--1 li:first-child');
        dh.autoHeight(dh.sPricing1Li);
    };

    // smoothScroll
    dh.smoothScroll = () => {
        $('a.smoothScroll').click(function () {
            if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') ||
                location.hostname == this.hostname) {
                var target = $(this.hash);
                target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
                if (target.length) {
                    $('html,body').animate({
                        scrollTop: target.offset().top
                    }, 1000);
                    return false;
                }
            }
        });
    };


    // plugins

    dh.plugins = () => {

        if (dh.popupVdo.length && $.fn.magnificPopup) {
            dh.popupVdo.magnificPopup({
                disableOn: 0,
                type: 'iframe',
                mainClass: 'mfp-fade',
                removalDelay: 160,
                preloader: true,
                fixedContentPos: false
            });
        }
        
        dh.mainMenu = $('.eco--main--menu');
        if($.fn.slicknav && dh.mainMenu.length){
            dh.mainMenu.slicknav({
                appendTo: '.eco--menu--col',
                allowParentLinks: true
            });
        }
    };

    dh.mailchimp_form = () => {
        dh.mcForm1 = $('.eco--mc--form1');
        if ($.fn.ajaxChimp) {
            if (dh.mcForm1.length) {
                let listURL = dh.mcForm1.attr('action');
                dh.submitSpinner = dh.mcForm1.find('button i');
                dh.mcSubmit1 = dh.mcForm1.find('[type=submit]');
                dh.mcInp1 = dh.mcForm1.find('input');
                dh.mcSubmit1.on('click', () => {
                    dh.submitSpinner.removeClass('hidden');
                });
                dh.mcForm1.ajaxChimp({
                    url: listURL,
                    callback: resp => {
                        if (resp.result === 'success') {
                            swal("Good job!", "Please check your email and verify!", "success");
                            dh.submitSpinner.addClass('hidden');
                            dh.mcInp1.val('');
                        } else {
                            swal("Oops!", "There was a problem with your submission. Please complete the form and try again.", "warning");
                            dh.submitSpinner.addClass('hidden');
                        }
                    }
                });
            }
        }

        dh.mcForm2 = $('.eco--mc--form2');
        if ($.fn.ajaxChimp) {
            if (dh.mcForm2.length) {
                let listURL = dh.mcForm2.attr('action');
                dh.submitSpinner2 = dh.mcForm2.find('button i');
                dh.mcSubmit2 = dh.mcForm2.find('[type=submit]');
                dh.mcInp2 = dh.mcForm2.find('input');
                dh.mcSubmit2.on('click', () => {
                    dh.submitSpinner2.removeClass('hidden');
                });
                dh.mcForm2.ajaxChimp({
                    url: listURL,
                    callback: resp => {
                        if (resp.result === 'success') {
                            swal("Good job!", "Please check your email and verify!", "success");
                            dh.submitSpinner2.addClass('hidden');
                            dh.mcInp2.val('');
                        } else {
                            swal("Oops!", "There was a problem with your submission. Please complete the form and try again.", "warning");
                            dh.submitSpinner2.addClass('hidden');
                        }
                    }
                });
            }
        }
    };

    // console notice
    dh.consoleTxt = () => {
        dh.consoleStyle = [
            'font-size: 10px',
            'color: #ffffff',
            'background-color: #2e7d32',
            'display: block',
            'text-align: left',
            'font-weight: bold',
            'display: inline-block'
        ].join(';');
        console.log('%c SITE LOADED 100%, - Created by ' + dh.dev, dh.consoleStyle);
    };

    dh.sliders = () => {

        if ($.fn.slick) {

            // review slider 1
            dh.reviewSlider1 = $('.eco--review--slider--1');
            if (dh.reviewSlider1.length) {
                dh.reviewSlider1.slick({
                    prevArrow: '<i class="fa fa-long-arrow-up eco--prev"></i>',
                    nextArrow: '<i class="fa fa-long-arrow-down eco--next"></i>',
                    vertical: true
                });
            }

            // review slider 2
            dh.reviewSlider2 = $('.eco--review--slider--2');
            if (dh.reviewSlider2.length) {
                dh.reviewSlider2.slick({
                    prevArrow: '<i class="fa fa-long-arrow-left eco--prev"></i>',
                    nextArrow: '<i class="fa fa-long-arrow-right eco--next"></i>'
                });
            }

            // brand slider 1
            dh.brandSlider1 = $('.eco--brand--slider--1');
            if (dh.brandSlider1.length) {
                dh.brandSlider1.slick({
                    prevArrow: false,
                    nextArrow: false,
                    slidesToShow: 5,
                    autoplay: true,
                    responsive: [
                        {
                            breakpoint: 768,
                            settings: {
                                slidesToShow: 2
                            }
                        },
                        {
                            breakpoint: 992,
                            settings: {
                                slidesToShow: 3
                            }
                        }
                    ]
                });
            }
        }
    };

    // all functions of document ready
    dh.docReady = () => {
        dh.fnPreloader();
        dh.sliders();
        dh.heightConfig();
        dh.smoothScroll();
        dh.plugins();
        dh.mailchimp_form();
    };

    // all functions of window load
    dh.winLoad = () => {
        dh.consoleTxt();
        dh.heightConfig();
    };


    $(document).ready(dh.docReady);
    $(window).on('load', dh.winLoad);



})(jQuery);
