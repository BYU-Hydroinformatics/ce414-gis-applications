// Header dropdowns: only one open at a time, and close on a click outside them or on Escape.
document.addEventListener("toggle", function (e) {
  if (!e.target.matches || !e.target.matches("details.ce-menu") || !e.target.open) return;
  document.querySelectorAll("details.ce-menu[open]").forEach(function (d) {
    if (d !== e.target) d.removeAttribute("open");
  });
}, true);
document.addEventListener("click", function (e) {
  document.querySelectorAll("details.ce-menu[open]").forEach(function (d) {
    if (!d.contains(e.target)) d.removeAttribute("open");
  });
});
document.addEventListener("keydown", function (e) {
  if (e.key !== "Escape") return;
  document.querySelectorAll("details.ce-menu[open]").forEach(function (d) { d.removeAttribute("open"); });
});
