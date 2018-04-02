function populateSearch() {
    var gamesInput = document.getElementById('gamesList');

    var gamesXHR = $.get( '/games', function() {
    }).done(function(data) {
        new Awesomplete(gamesInput, {
            list: data['games']
        });
        gamesInput.focus();
    }).fail(function() {
        console.log('Could not load /games list.');
    });
    $("#gamesList").on("awesomplete-close", function(e){
        if (e.originalEvent.reason == 'select') {
            searchVODs();
        }
    });
}

function hookKeypress() {
    $('#gamesList').keypress(function (e) {
        if (e.which == 13) { // Enter key
            searchVODs();
        }
    });
}

function searchVODs() {
    var searchQuery = $.trim($('#gamesList').val());
    if (searchQuery != '') {
        var searchXHR = $.post( '/search', {'data': searchQuery}, function() {
        }).done(function(data) {
            //console.log(data['vods']);
            parseResults(data);
        }).fail(function() {
            console.log('Could not search.');
        });
    }
}

function parseResults(data) {
    /*
        game_index, date, vod_id, start_at
    */

    $('#resultsNav').pagination({
        dataSource: data['vods'],
        pageSize: 9,
        showPageNumbers: false,
        showNavigator: true,
        callback: function(paginatedData, pagination) {
            $('#results').html(' ');
            $.each(paginatedData, function(i, vod) {
                var articleEl = $(document.createElement('article'));
                var divEl = $(document.createElement('div'));
                var spanGameEl = $(document.createElement('span'));
                var spanDateEl = $(document.createElement('span'));

                var gameName = data['games'][vod['game_index']][1];

                divEl.addClass('info');
                if (i % 2 == 0) {
                    articleEl.addClass('alt');
                }

                spanGameEl.text(gameName + ': ');
                spanDateEl.text(new Date(vod['date']).toString());

                divEl.append(spanGameEl);
                divEl.append(spanDateEl);

                articleEl.append(divEl);
                articleEl.click(function() {
                    window.open('https://www.twitch.tv/videos/' + vod['vod_id'] + '?t=' + vod['start_at'] + 's', '_blank');
                });

                $('#results').append(articleEl)

                //console.log( articleEl );
            });
        }
    });
    /*
    var gamesData = data['games'];
    var vodsData = data['vods'];
    */

    /*
    var event = new Date("2016-12-28T22:46:26Z");
    console.log(event.toString());
    */
}

$(function() {
    populateSearch();
    hookKeypress();
});