var touchVal = null;
document.addEventListener('touchstart', function (e){
    if (e.touches.length === 1) {
        touchVal = e.touches.item(0).clientX;
    } else {
        touchVal = null;
    }
});

document.addEventListener('touchend', function (e) {
    var offset = 100;
    if (touchVal) {
        var touchEnd = e.changedTouches.item(0).clientX;
        if (touchEnd < touchVal - offset) {
            if ($('#resultsNav').pagination('getSelectedPageNum') == 1) {
                $('#resultsNav').pagination('go', $('#resultsNav').pagination('getTotalPage'));
            } else {
                $('#resultsNav').pagination('previous');
            }
        } else if (touchEnd > touchVal + offset) {
            if ($('#resultsNav').pagination('getSelectedPageNum') == $('#resultsNav').pagination('getTotalPage')) {
                $('#resultsNav').pagination('go', 1);
            } else {
                $('#resultsNav').pagination('next');
            }
        }
    }
});