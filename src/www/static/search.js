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
        } else if (e.originalEvent.reason == 'nomatches' || e.originalEvent.reason == 'esc') {
            clearHash();
        }
    });
}

function hookKeypress() {
    $('#gamesList').keydown(function (e) {
        if (e.which == 13) { // Enter key
            searchVODs();
            $('.awesomplete ul').attr('hidden','hidden');
        } else if (e.which == 27) { // Esc key
            $('#gamesList').val('');
            clearHash();
        }
    });
    $('#gamesList').on('input', function (e) {
        if ($('#gamesList').val().length == 0) {
            clearHash();
        }
    });

    $(document).keydown(function (e) {
        if (!$('#gamesList').is(':focus')) {
            if (e.which == 37) { // Left arrow key
                if ($('#resultsNav').pagination('getSelectedPageNum') == 1) {
                    $('#resultsNav').pagination('go', $('#resultsNav').pagination('getTotalPage'));
                } else {
                    $('#resultsNav').pagination('previous');
                }
            } else if (e.which == 39) { // Right arrow key
                if ($('#resultsNav').pagination('getSelectedPageNum') == $('#resultsNav').pagination('getTotalPage')) {
                    $('#resultsNav').pagination('go', 1);
                } else {
                    $('#resultsNav').pagination('next');
                }
            }
        }
    });

    $(document).keyup(function (e) {
        if (!$('#gamesList').is(':focus')) {
            if (e.which == 9 || e.which == 191) {  // Tab, / keys respectively
                $('#gamesList').select();
            }
        }
    });

}

function initHash() {
    if (window.location.hash.length > 0) {
        $('#gamesList').val(unescape($.trim(window.location.hash.slice(1))));
        searchVODs();
    }
}

function clearHash() {
    window.location.hash = '';
}

function searchVODs() {
    var searchQuery = $.trim($('#gamesList').val());
    if (searchQuery != '') {
        var searchXHR = $.post( '/search', {'data': searchQuery}, function() {
        }).done(function(data) {
            //console.log(data['vods']);
            parseResults(data);
            window.location.hash = searchQuery;
        }).fail(function() {
            console.log('Could not search.');
            $('#gamesList').val('There was an error. :(');
        });
    }
}

function addBoxart(game) {
    var imgEl = $(document.createElement('img'));
    imgEl.attr('src', 'https://static-cdn.jtvnw.net/ttv-boxart/' + game + '-140x185.jpg');
    imgEl.attr('title', decodeURI(game));
    imgEl.click(function() {
        $('#gamesList').val(decodeURI(game));
        searchVODs();
    });

    $('#boxart').append(imgEl);
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
            var gamesListed = {};
            if (pagination.totalNumber > pagination.pageSize) {
                $('#gamesList').blur();
            }
            $('#results').html(' ');
            $('#boxart').html(' ');
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

                $('#results').append(articleEl);

                if (!(vod['game_index'] in gamesListed)) {
                    gamesListed[vod['game_index']] = true;
                    addBoxart(encodeURI(gameName));
                }
            });
        }
    });
}

$(function() {
    populateSearch();
    hookKeypress();
    initHash();
});