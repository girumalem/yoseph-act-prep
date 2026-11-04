# Yoseph's ACT Prep

Study app (vocab, English, math, weekly goal) and Dad's dashboard, hosted on Netlify.

- `public/index.html`: the student app
- `public/dad/index.html`: Dad's dashboard (PIN required)
- `netlify/functions/progress.mts`: saves and serves progress (Netlify Blobs)

## Brooke (6th grade)

- `public/brooke/index.html`: Brooke's Study Quest (built, don't edit by hand)
- `content/brooke/`: her vocabulary, math, and English questions
- Rebuild after editing content: `python3 tools/build_brooke.py content/brooke`

The dashboard at `/dad/` switches between Brooke and Yoseph. Each app saves under its own name (`?student=`).
