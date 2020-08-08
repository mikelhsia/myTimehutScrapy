(function() {
    if (window.myBookmarklet !== undefined) {
        myBookmarklet();
    } else {
        /* TODO: the bookmarklet.js can't be found */
        document.body.appendChild(document.createElement('script')).src='http://127.0.0.1:8000/images/static/js/bookmarklet.js?r=' + Math.floor(Math.random() * 99999999999);
    }
})();
