# Section-divider art

Every `lead` section-divider slide carries one image in anime style, placed right after the lead
comment:

```markdown
<!-- _class: lead -->
![bg right:55%](images/<id>.jpg)
```

Each JSON file here lists the scene prompt for every divider image in a set of decks:
`week01-08-anime.json`, `week09-anime.json` and `week10-12-anime.json`. The scene prompts omit the
style; every image gets the same style suffix:

> — Modern Japanese anime film still, full color: clean cel shading, soft painterly backgrounds with
> luminous skies and atmospheric light, expressive adult characters with realistic proportions,
> cinematic composition, vivid but natural palette. Absolutely no text, speech bubbles, sound effects,
> signs, words, letters or numbers anywhere in the image.

Generated with the OpenAI images skill (`gpt-image-2.5-flare`, medium quality, 1024 × 1024) and saved
into the deck's `images/` folder as JPEG at quality 85.

When writing a new prompt:

- Describe the idea of the section as a scene with adult characters, not a joke or a meme.
- Give about half of the solo scenes a woman lead; left unspecified, the model draws men.
- Look at every image for stray lettering before it goes in a deck.

The anime images replaced meme-style cartoons (Weeks 8 and 9) and a brief manga set (Weeks 10 to 12)
on October 27, 2026; their prompt files are in the git history.
