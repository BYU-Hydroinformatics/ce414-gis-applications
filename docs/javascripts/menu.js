// Close the header "Menu" dropdown on a click outside it or on Escape.
document.addEventListener("click", function (e) {
  document.querySelectorAll("details.ce-menu[open]").forEach(function (d) {
    if (!d.contains(e.target)) d.removeAttribute("open");
  });
});
document.addEventListener("keydown", function (e) {
  if (e.key !== "Escape") return;
  document.querySelectorAll("details.ce-menu[open]").forEach(function (d) { d.removeAttribute("open"); });
});
