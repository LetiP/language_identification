$(document).ready(function () {
    $('#find_out').on('click', function () {
        $('.loading-overlay').fadeIn();
        var txt = $('#text_sample').val();
        console.log(txt);
        toPython = new Object();
        toPython.txt = txt;
        $.ajax({
            url: "/identifyLang",
            data: JSON.stringify(toPython, null, "\t"),
            type: "POST",
            contentType: "application/json;charset=UTF-8",
            success: function (response) {
                var response = JSON.parse(response);
                console.log(response);
                var map = {
                    'deu': 'Deutsch',
                    'eng': 'English',
                    'ron': 'Română',
                    'swe': 'Swedish',
                    'fra': 'Français',
                    'tur': 'Turkish',
                    'ita': 'Italian',
                    'spa': 'Spanish',
                    'pol': 'Polski'
                }
                $('#inferred_lan').text(map[response['language']]);
                $('.loading-overlay').fadeOut();
                $('#inferred_lan').fadeIn();
            }
        });
    });



    $("body").on("click", ".fa-chevron-down", function () {
        $(".contact").slideDown();
        $(this).removeClass("fa-chevron-down");
        $(this).addClass("fa-chevron-up");
    });
    $("body").on("click", ".fa-chevron-up", function () {
        $(".contact").slideUp();
        $(this).removeClass("fa-chevron-up");
        $(this).addClass("fa-chevron-down");
    });
});