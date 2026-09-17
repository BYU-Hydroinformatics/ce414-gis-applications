/* CE 414 lecture quizzes — shared engine.
   A quiz page loads this file and calls CE414Quiz.start({...}) with its own questions.
   Nothing here knows anything about a particular lecture; see tools/lecture-quiz-guide.md
   for the authoring rules and the shape of the data object. */
(function (global) {
  "use strict";

  var KEY_LABELS = ["1", "2", "3", "4"];

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }

  function start(spec) {
    var questions = spec.questions || [];
    if (!questions.length) throw new Error("CE414Quiz: no questions supplied");

    var root = document.getElementById("quizRoot");
    var index = 0;
    var score = 0;
    var answered = false;
    var missed = [];

    // --- chrome -------------------------------------------------------------
    var head = el("header");
    var h1 = el("h1", null, spec.title);
    var sub = el("p", "subtitle");
    sub.innerHTML = spec.subtitle || "";
    head.appendChild(h1);
    head.appendChild(sub);

    var scoreBar = el("div", "score-bar");
    scoreBar.id = "scoreBar";
    var progressText = el("span", null, "");
    var scoreText = el("span", null, "Score: 0 / 0");
    scoreBar.appendChild(progressText);
    scoreBar.appendChild(scoreText);

    var track = el("div", "progress-track");
    var fill = el("div", "progress-fill");
    track.appendChild(fill);

    var card = el("div", "quiz-card");
    var content = el("div");
    var badge = el("div", "question-badge", spec.badge || "Question");
    var prompt = el("div", "question-prompt");
    var detail = el("div", "question-detail");
    var options = el("div", "options");
    var feedback = el("div", "feedback");
    feedback.setAttribute("role", "status");
    feedback.setAttribute("aria-live", "polite");
    var controls = el("div", "controls");
    var nextBtn = el("button", "next-btn", "Next");
    nextBtn.type = "button";
    controls.appendChild(nextBtn);

    var kbdHint = el("span", "kbd-hint", "Tip: press 1-4 to answer, Enter to continue.");

    content.appendChild(badge);
    content.appendChild(prompt);
    content.appendChild(detail);
    content.appendChild(options);
    content.appendChild(feedback);
    content.appendChild(controls);
    content.appendChild(kbdHint);

    var final = el("div", "final-screen");
    var finalH = el("h2", null, "Quiz complete");
    var finalScore = el("div", "final-score");
    var finalNote = el("p", "final-note");
    var review = el("div", "review");
    var restart = el("button", "restart-btn", "Start over");
    restart.type = "button";
    final.appendChild(finalH);
    final.appendChild(finalScore);
    final.appendChild(finalNote);
    final.appendChild(review);
    final.appendChild(restart);

    card.appendChild(content);
    card.appendChild(final);

    var foot = el("footer", "page-foot");
    foot.innerHTML = 'CE 414 Engineering Applications of GIS &middot; <a href="../../">Course site</a>' +
      (spec.deckUrl ? ' &middot; <a href="' + spec.deckUrl + '">the slides this came from</a>' : "") +
      '<br>Practice only — nothing here is recorded or graded.';

    root.appendChild(head);
    root.appendChild(scoreBar);
    root.appendChild(track);
    root.appendChild(card);
    root.appendChild(foot);

    // --- behavior -----------------------------------------------------------
    var buttons = [];

    function loadQuestion() {
      answered = false;
      var q = questions[index];

      badge.textContent = q.badge || spec.badge || "Question";
      prompt.textContent = q.prompt;
      detail.textContent = q.detail || "";
      detail.style.display = q.detail ? "block" : "none";

      options.innerHTML = "";
      options.className = "options" + (q.options.length !== 2 || longOptions(q) ? " stacked" : "");
      buttons = q.options.map(function (text, i) {
        var b = el("button", "opt-btn");
        b.type = "button";
        var hint = el("span", "key-hint", KEY_LABELS[i] + ".");
        b.appendChild(hint);
        b.appendChild(document.createTextNode(text));
        b.addEventListener("click", function () { answer(i); });
        options.appendChild(b);
        return b;
      });

      feedback.className = "feedback";
      feedback.innerHTML = "";
      nextBtn.style.display = "none";

      progressText.textContent = "Question " + (index + 1) + " of " + questions.length;
      fill.style.width = (index / questions.length) * 100 + "%";
    }

    function longOptions(q) {
      return q.options.some(function (o) { return o.length > 22; });
    }

    function answerIndex(q) {
      return typeof q.answer === "number" ? q.answer : q.options.indexOf(q.answer);
    }

    function answer(choice) {
      if (answered) return;
      answered = true;

      var q = questions[index];
      var correct = answerIndex(q);
      var isRight = choice === correct;
      if (isRight) score++;
      else missed.push({ prompt: q.prompt, answer: q.options[correct], explanation: q.explanation });

      scoreText.textContent = "Score: " + score + " / " + (index + 1);

      buttons.forEach(function (b) { b.disabled = true; });
      buttons[choice].classList.add(isRight ? "correct" : "incorrect");
      if (!isRight) buttons[correct].classList.add("correct");

      feedback.className = "feedback visible " + (isRight ? "correct-box" : "incorrect-box");
      var headline = isRight ? "✓ Correct" : "✗ Not quite — the answer is " + q.options[correct];
      feedback.innerHTML = "";
      var strong = el("strong", null, headline);
      feedback.appendChild(strong);
      feedback.appendChild(document.createTextNode(q.explanation));

      nextBtn.textContent = index === questions.length - 1 ? "See how you did" : "Next question →";
      nextBtn.style.display = "inline-block";
      nextBtn.focus();
      fill.style.width = ((index + 1) / questions.length) * 100 + "%";
    }

    function next() {
      index++;
      if (index < questions.length) loadQuestion();
      else showResults();
    }

    function showResults() {
      content.style.display = "none";
      scoreBar.style.display = "none";
      track.style.display = "none";
      final.style.display = "block";
      finalScore.textContent = score + " / " + questions.length;

      var pct = score / questions.length;
      finalNote.textContent = pct === 1 ? (spec.perfectNote || "A perfect score — nothing here to review.")
        : pct >= 0.7 ? (spec.goodNote || "Solid. Read the explanations for the ones you missed.")
        : (spec.tryAgainNote || "Worth another pass — the explanations below are the short version of the lecture.");

      review.innerHTML = "";
      if (missed.length) {
        review.appendChild(el("h3", null, "What to look at again"));
        var ol = el("ol");
        missed.forEach(function (m) {
          var li = el("li");
          li.appendChild(el("strong", null, m.prompt));
          var span = el("span", "ans", m.answer + " — ");
          li.appendChild(span);
          li.appendChild(document.createTextNode(m.explanation));
          ol.appendChild(li);
        });
        review.appendChild(ol);
      }
      restart.focus();
    }

    function restartQuiz() {
      index = 0;
      score = 0;
      missed = [];
      content.style.display = "block";
      scoreBar.style.display = "flex";
      track.style.display = "block";
      final.style.display = "none";
      scoreText.textContent = "Score: 0 / 0";
      loadQuestion();
    }

    nextBtn.addEventListener("click", next);
    restart.addEventListener("click", restartQuiz);

    document.addEventListener("keydown", function (e) {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      if (final.style.display === "block") return;
      var n = KEY_LABELS.indexOf(e.key);
      if (n >= 0 && !answered && n < buttons.length) {
        e.preventDefault();
        answer(n);
      } else if ((e.key === "Enter" || e.key === " ") && answered) {
        // Advance from here rather than leaving it to the focused button's own default
        // action, and suppress that default so one key press never advances twice.
        e.preventDefault();
        next();
      }
    });

    loadQuestion();
  }

  global.CE414Quiz = { start: start };
})(window);
