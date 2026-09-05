// Open external links (and file downloads) from page content in a new tab, so a student
// following a lab keeps their place while a data portal or reference page opens.
(function () {
  function retarget() {
    document.querySelectorAll(".md-content a[href]").forEach(function (a) {
      var url;
      try { url = new URL(a.getAttribute("href"), window.location.href); } catch (e) { return; }
      var external = url.origin !== window.location.origin;
      var download = /\.(zip|pdf|docx|xlsx|pptx|gdb|shp)$/i.test(url.pathname);
      if (external || download) {
        a.setAttribute("target", "_blank");
        a.setAttribute("rel", "noopener");
      }
    });
  }
  if (typeof document$ !== "undefined") { document$.subscribe(retarget); } else { document.addEventListener("DOMContentLoaded", retarget); }
})();
