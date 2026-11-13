# Safe House Church vertical shorts

How the weekly shorts are made (used by the Sunday and Wednesday content-prep tasks).

1. **Find the moment.** Get the service or Bible study transcript from Restream (`list_event_transcriptions` → `get_event_transcript`). Pick a 45–90 second passage that stands on its own, with a strong opening line and a clean ending.
2. **Cut a 1080p master clip.** Get the recording URL from Restream (`list_user_recordings` → `get_recording_download_url`). In Picsart, `picsart_media_export` a 1920x1080, 30 fps scene holding one media layer with `trim: {in, out}` (the source seconds), `fit: "contain"`, and a duration that is a multiple of 1/30. The transcript timestamps can be off by 1–2 seconds, so pad 2 seconds on each side the first time.
3. **Get word timings.** Run `picsart_media_transcribe` on the master clip with `include: ["transcript", "words"]`. If the clip starts or ends mid-sentence, re-cut it using the word times, then transcribe again.
4. **Build the scene.** Write a config file (see the docstring in `make_scene.py`) and run `python3 tools/shorts/make_scene.py cfg.json media/scenes/<slug>.json`. Music: only use real recorded tracks that Pastor Matthew approved, listed in `media/music/tracks.json` with a mood for each. Match the track to the clip: uplifting or hopeful for encouragement, steady or building for teaching. Never use sad or somber tracks, and never synthesize music. If no track has been approved, leave `music` out and the short is voice only.
5. **Host the scene.** Commit and push it, then use `https://raw.githubusercontent.com/safehousephx-church/safehouse-church/<commit sha>/media/scenes/<slug>.json` as the scene URL. Use the commit SHA, not `main`, because GitHub caches `main`.
6. **Check, then render.** Run `picsart_media_validate_scene`, then `picsart_media_contact_sheet` at two moments to check the layout. Then run `picsart_media_export` (MP4, 1080x1920).

Layout: logo top center; a two-line headline (white, then gold); the video as a 1080x1080 center crop over a blurred, darkened copy of itself; word-by-word captions with the spoken word in gold; a two-line footer; and, when an approved track exists, music under his voice (volume about 14) that fades in and out.
