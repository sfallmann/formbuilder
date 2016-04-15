(function(){

    String.prototype.replaceAll = function(
        strTarget, // The substring you want to replace
        strSubString // The string you want to replace in.
        ){
        var strText = this;
        var intIndexOfMatch = strText.indexOf( strTarget );

        // Keep looping while an instance of the target string
        // still exists in the string.
        while (intIndexOfMatch != -1){
            // Relace out the current instance.
            strText = strText.replace( strTarget, strSubString )

            // Get the index of any next matching substring.
            intIndexOfMatch = strText.indexOf( strTarget );
        }

        // Return the updated string with ALL the target strings
        // replaced out with the new substring.
        return( strText );
    }

    window.callback = function() {
        grecaptcha.render('id-g-recaptcha', {
         'sitekey': "6LcyMBoTAAAAAOLSi90hQ33PFhQg6ejClya9Vv88",
         'expired-callback': expCallback
        });
    };
    window.expCallback = function() {

        grecaptcha.reset();
    };

    // delay setting all elemnts to visible to allow the page to be fully loaded before displaying
    $(document).ready(function() {

        var showPage = function(){
            document.getElementsByTagName("body")[0].style.visibility = "visible";
        }

        setTimeout(showPage, 500);

    });

    window.fb = {

        $form: $("#fb-form"),
        $submit: $("#submit-id-submit"),
        $errors: $("#error-div"),
        $phoneSelects: $("input[type=tel]"),
        $popupTarget: $("#popupTarget"),
        $popup: $("<div/>", { id: "popup" }),
        maxFiles: function(){

            return parseInt($("#dzMaxFiles").val());

        },
        getCookie: function (name)
        {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?

                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        },
        clearErrors: function(){
            fb.$errors.empty();
        },
        displayError: function(message){

            var html =  '<div class="alert alert-danger">' +
                        '<a class="close" data-dismiss="alert">×</a>' +
                        '<strong>' + message + '</strong>'
                        '</div>';

            console.log(message);
            fb.$errors.append(html);
        },
        initPopup: function(){

            fb.$popupTarget.append(fb.$popup);

            fb.$popup.bPopup({

                escClose: false,
                modalClose: false

            });

        },
        recaptchaCheck: function(){

            console.log("initiate reCaptcha check");

            var target = fb.$popup[0];

            fb.initPopup();
            fb.spinner.spin(target);

            $.ajax(
                {
                    url: "/ajax/recaptcha_check/",
                    method: "POST",
                    data: { "g-recaptcha-response": $("#g-recaptcha-response").val() },
                    beforeSend: function(xhr, settings) {
                        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                            xhr.setRequestHeader("X-CSRFToken", fb.getCookie('csrftoken'));
                        }
                    },
                    success: function(response){



                        if (response.success){

                            fb.$form.trigger("recaptcha:success");
                        }
                        else {

                            fb.$form.trigger("recaptcha:fail", response);
                        }
                    },
                    error: function(xhr){

                        fb.$popup.close();
                        fb.spinner.stop();

                        var messsage = "There was a problem sending the recaptcha check to the server";
                        fb.displayError(message);

                    }
                });



        },

        init: function(){
            fb.$submit.removeAttr("disabled");
            $(".accordion-toggle").addClass("collapsed").attr("aria-expanded","false");
            $(".panel-collapse.collapse.in").removeClass("in").attr("aria-expanded","false");

            var spinOpts = {
                  lines: 16 // The number of lines to draw
                , length: 10 // The length of each line
                , width: 8 // The line thickness
                , radius: 60 // The radius of the inner circle
                , scale: 1.5 // Scales overall size of the spinner
                , corners: 1 // Corner roundness (0..1)
                , color: '#FFFFFF' // #rgb or #rrggbb or array of colors
                , opacity: 0.50 // Opacity of the lines
                , rotate: 0 // The rotation offset
                , direction: 1 // 1: clockwise, -1: counterclockwise
                , speed: 1.0 // Rounds per second
                , trail: 60 // Afterglow percentage
                , fps: 20 // Frames per second when using setTimeout() as a fallback for CSS
                , zIndex: 2e9 // The z-index (defaults to 2000000000)
                , className: 'spinner' // The CSS class to assign to the spinner
                , top: '50%' // Top position relative to parent
                , left: '50%' // Left position relative to parent
                , shadow: false // Whether to render a shadow
                , hwaccel: false // Whether to use hardware acceleration
                , position: 'absolute' // Element positioning
                }

            fb.spinner = new Spinner(spinOpts);

            function verifyTel(input) {

                input = input.srcElement;


                if ($.trim(input.value)) {
                    if (!($(input).intlTelInput("isValidNumber"))) {

                        console.log("invalid number");

                        var pattern = $(input).attr("placeholder");

                        input.setCustomValidity('Please enter the phone number like this: ' + pattern);

                    } else {

                        input.setCustomValidity('');
                    }
                }
            }

            fb.$phoneSelects.each(function(index, el){

                var id = $("#" + $(el).attr("id"));

                id.intlTelInput({
                    utilsScript: "/static/intl-tel-input/build/js/utils.js"
                });

                id[0].addEventListener("blur", verifyTel);

                fb.$submit.click(function(){
                    id[0].checkValidity();
                }); //true)

            });

            fb.$form.on("submit", function(e){

                fb.clearErrors();
                e.preventDefault();
                fb.recaptchaCheck();

            });


        }

    };

    fb.init();

}());

