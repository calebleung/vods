var gamesList = []

function initConfig() {
    if (typeof(channelName) == 'undefined') {
        return;
    }

    document.title = channelName + ' ' + document.title;

    var aEl = document.createElement('a');
    aEl.href = channelURL;
    aEl.target = '_blank';

    var channelAnchorEl = document.createElement('a');
    channelAnchorEl.href = channelURL;
    channelAnchorEl.target = '_blank';

    $(channelAnchorEl).text(channelName);

    var imgEl = document.createElement('img');
    imgEl.style.width = '50%';
    imgEl.style.height = '50%';
    imgEl.src = channelLogo;

    aEl.append(imgEl);

    $('#channelLogo').append(aEl);
    $('#channelName').html(channelAnchorEl);

    if (window.location.hash.length == 0) {
        showInfo();
    }
    populateDropdown();
}

function populateDropdown() {
    $.each(gamesList, function(i, game) {
        var optionEl = document.createElement('option');
        if (game != '') {
            optionEl.value = game;
            optionEl.text = game;
            $('#gamesDropdown').append(optionEl);
        }
    });
    $('#gamesDropdown').change(function() {
        $('#gamesList').val($('#gamesDropdown option:selected').val());
        searchVODs();
    });
}

function showInfo() {
    $('#results').html(' ');
    $('#boxart').html(' ');
    $('#channelInfo').show();
}

function populateSearch() {
    var gamesInput = document.getElementById('gamesList');

    var gamesXHR = $.get( '/games', function() {
    }).done(function(data) {
        gamesList = data['games'];
        new Awesomplete(gamesInput, {
            list: gamesList
        });
        gamesInput.focus();
        initConfig();
    }).fail(function() {
        $('#results').html('Could not load /games list.');
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
            } else if (e.which == 191) {  // / key
                e.preventDefault();       // Prevents a '/' in input and Quick Search in Firefox
                $('#gamesList').select();
            } else if (e.which == 27) { // Esc key
                $('#gamesList').val('');
                $('#gamesList').select();
                searchVODs();
                clearHash();
            }
        }
    });

}

function initHash() {
    if (window.location.hash.length > 0) {
        $('#gamesList').val(unescape($.trim(window.location.hash.slice(1))));
        $('#channelInfo').hide();
        searchVODs();
    }
}

function clearHash() {
    window.location.hash = '';
}

function searchVODs() {
    var searchQuery = $.trim($('#gamesList').val());
    if (searchQuery != '') {
        $('#results').html('Searching...');
        $('#channelInfo').hide();

        var searchXHR = $.post( '/search', {'data': searchQuery}, function() {
        }).done(function(data) {
            //console.log(data['vods']);
            parseResults(data);
            window.location.hash = searchQuery;
        }).fail(function() {
            console.log('Could not search.');
            $('#results').val('There was an error. :(');
        });
    } else {
        $('#resultsNav').pagination('disable');
        $('#resultsNav').pagination('hide');
        showInfo();
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
            if (pagination.totalNumber == 0) {
                $('#results').html('No VODs found!');
            }
        }
    });
}

$(function() {
    populateSearch();
    hookKeypress();
    initHash();
});