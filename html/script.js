function scroll(aid) {
    $(document).scrollTop($(aid).offset().top)
}

var results = []

function get_title(url) {
    return $.ajax({
        type: "GET",
        url: '/api/v1/get_title',
        data: {
            'url': url
        },
        async: false
    }).responseText;

}


function jobresult() {
    $.ajax({
        type: 'GET',
        url: "/api/v1/job_result",
        data: {
            'id': window.jobid,
        },
        success: function(result) {
            if (result.broken) {
                html = '<p class="error-details">Error: <span class="highlight">' + result.error + '</span> on line <span class="highlight">' + result.lineno + '</span></p><br><br><h2 class="gradient-text title bold">Results</h2>'
            } else {
                html = ''
            }
            $("#results").css("display", "block");
            $("#intro").css("display", "none");
            if (result.broken) {
                console.log(result);
                for (var i = 0; i < result.links.length; i++) {
                    item = result.links[i];
                    if (item.source.includes('stackoverflow')) {
                        source = "stackoverflow"
                    } else {
                        source = item.source
                    }
                    element = '<div class="box-dark"><span class="icon-' + source + '"></span><span class="list-count">' + (i + 1) + '</span><a href="' + item.url + '" target="_blank"><h3 class="dark-gradient">' + item.title + '</h3></a> <p class="p1">' + item.source + '</p><br><br><br> </div>';
                    html += element;
                }
            } else {
                html += '<div class="box-dark"><h3 class="dark-gradient">Your code isn\'t broken! </h3> <p class="p1">Our analysis found no problem.</p> <p class="p2">You might want to check: <ul><li>if you used tabs correctly</li><li>if you included your whole file</li><li>what version of python you are running as it may make the whole script run differently</li><li>did you install all modules with pip?</li></ul><br><br><br><br></p></div>';
            }
            html += '<br><br><br><br><br><br><br><br>';
            $('#results').html(html);
            $("button").prop("disabled", false);
            $('body').toggleClass('loading')
            scroll('#results-anchor')



        }
    });
}


function checkjob(client_job) {
    $.ajax({
        type: 'GET',
        url: "/api/v1/job_status",
        data: {
            'id': window.jobid,
        },
        success: function(result) {
            console.log(result)
            status = result.status
            if ($(".status-buffer").text() != result.msg) {
                console.log("------")
                console.log($(".status-buffer").text())
                console.log(result.msg)
                $(".status-buffer").text(result.msg)
                $(".status").fadeOut(function() {
                    $(this).text(result.msg)
                }).fadeIn();
            }

            if (status == "Finished") {
                clearInterval(client_job);
                setTimeout(function() {
                    jobresult()
                }, 800);
            }



        }
    });
}

function analyse() {
    $("button").prop("disabled", true);
    $('body').toggleClass('loading')
    results = []
    $.ajax({
        type: 'GET',
        url: "/api/v1/analyse",
        data: {
            'code': $('textarea').val(),
        },
        success: function(result) {
            window.jobid = result.job
            client_job = 0;
            client_job = setInterval(function() { checkjob(client_job) }, 100);
        }
    });
}