(function(){

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

        setTimeout(showPage, 250);

    });

    window.fb = {

        $form: $("#fb-form"),
        $submit: $("#submit-id-submit"),
        $errors: $("#error-div"),
        $phoneSelects: $("input[type=tel]"),
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
        recaptchaCheck: function(){

            console.log("initiate reCaptcha check");

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
                        var messsage = "There was a problem sending the recaptcha check to the server"
                        fb.displayError(message);
                    }
                });
        }

    };

    $(".accordion-toggle").addClass("collapsed").attr("aria-expanded","false");
    $(".panel-collapse.collapse.in").removeClass("in").attr("aria-expanded","false");

    fb.$phoneSelects.each(function(index, el){

        var id = "#" + $(el).attr("id");

        $(id).intlTelInput();
    });

    fb.$submit.on("click", function(e){

        fb.clearErrors();

        e.stopPropagation();
        e.preventDefault();

        fb.recaptchaCheck();

    });

}());

