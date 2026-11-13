mergeInto(LibraryManager.library, {
    NotifyTrainingCompleted: function (tokenStr) {
        var token = UTF8ToString(tokenStr);
        console.log("[PhishAware WebGL] Egitim tamamlandi sinyali alindi: " + token);
        if (window.parent && window.parent.onUnityEgitimTamamlandi) {
            window.parent.onUnityEgitimTamamlandi(token);
        } else if (window.onUnityEgitimTamamlandi) {
            window.onUnityEgitimTamamlandi(token);
        } else {
            fetch('/egitim-tamamla/' + encodeURIComponent(token), { method: 'POST' })
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    console.log("[PhishAware] Backend egitim basariyla onaylandi:", data);
                })
                .catch(function(err) {
                    console.error("[PhishAware] Egitim onaylanirken hata:", err);
                });
        }
    }
});
