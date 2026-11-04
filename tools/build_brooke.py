"""Build public/brooke/index.html from Yoseph's app (public/index.html) plus Brooke's content.

Usage: python3 tools/build_brooke.py <content_dir>
content_dir holds brooke_vocab.py (V), brooke_math.py (M), brooke_english.py (E).
"""
import json, sys, re, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
content = pathlib.Path(sys.argv[1])
src = (root / "public/index.html").read_text()

def load(name, var):
    ns = {}
    exec((content / name).read_text(), ns)
    return ns[var]

V = load("brooke_vocab.py", "V")
M = load("brooke_math.py", "M")
E = load("brooke_english.py", "E")

words = [[w, p, d, a, b] for (w, p, d, a, b) in V]
words.sort(key=lambda x: x[0])
mcats = ["Ratios & Rates", "Number System", "Expressions & Equations", "Geometry", "Statistics"]
problems = []
for cat, q, ch, ex, _chk, why in M:
    problems.append([cat, q, ch, 0, ex, {ch[k]: why[k - 1] for k in (1, 2, 3)}])
eng = [[e[0], e[1], e[2], e[3], e[4], e[5], (e[6] if len(e) > 6 else "")] for e in E]
ecats = ["Punctuation", "Capitalization & Spelling", "Pronouns & Grammar", "Sentence Structure", "Word Choice & Context Clues"]
formulas = [
 ["Ratios & Rates","Unit rate","amount ÷ number of units","36 miles in 3 hours = 12 miles per hour."],
 ["Ratios & Rates","Equivalent ratios","Multiply or divide both parts by the same number","2 : 3 = 4 : 6 = 10 : 15."],
 ["Ratios & Rates","Percent","part ÷ whole × 100","18 out of 20 = 90%."],
 ["Ratios & Rates","Percent of a number","change the percent to a decimal, then multiply","25% of 80 = 0.25 × 80 = 20."],
 ["Number System","Dividing fractions","Keep, change, flip: a/b ÷ c/d = a/b × d/c","3/4 ÷ 1/2 = 3/4 × 2 = 1½."],
 ["Number System","Multiplying fractions","multiply the tops, multiply the bottoms","2/3 × 3/5 = 6/15 = 2/5."],
 ["Number System","GCF and LCM","GCF: biggest shared factor. LCM: smallest shared multiple","GCF(18, 24) = 6. LCM(4, 6) = 12."],
 ["Number System","Absolute value","distance from 0, always positive","|−7| = 7."],
 ["Number System","Coordinate plane quadrants","I (+,+)  II (−,+)  III (−,−)  IV (+,−)","(−3, 5) is in Quadrant II."],
 ["Expressions & Equations","Order of operations","Parentheses, Exponents, Multiply/Divide (left to right), Add/Subtract (left to right)","3² + 4 × 2 = 9 + 8 = 17."],
 ["Expressions & Equations","Distributive property","a(b + c) = ab + ac","3(x + 4) = 3x + 12."],
 ["Expressions & Equations","Solving equations","undo with the opposite operation on both sides","x + 9 = 23 → x = 14. 6y = 42 → y = 7."],
 ["Geometry","Rectangle and parallelogram area","A = base × height","8 × 5 = 40."],
 ["Geometry","Triangle area","A = ½ × base × height","½ × 10 × 6 = 30."],
 ["Geometry","Trapezoid area","A = ½(b₁ + b₂) × h","½(6 + 10) × 4 = 32."],
 ["Geometry","Volume of a rectangular prism","V = length × width × height","4 × 3 × 2 = 24 cubic units."],
 ["Geometry","Surface area of a prism","add the areas of all 6 faces","Cube with edge 3: 6 × 9 = 54."],
 ["Statistics","Mean","add the values, divide by how many","(4 + 8 + 6 + 10 + 7) ÷ 5 = 7."],
 ["Statistics","Median and mode","median: middle value when sorted. Mode: most frequent value","3, 6, 9, 12, 15 → median 9."],
 ["Statistics","Range and IQR","range = max − min. IQR = Q3 − Q1","Range of 9 to 30 is 21."],
 ["Statistics","Mean absolute deviation (MAD)","average distance of each value from the mean","2, 4, 6, 8: mean 5, MAD 2."],
]

h = src

def rep(a, b, count=1):
    global h
    n = h.count(a)
    assert n == count, f"expected {count} of {a[:70]!r}, found {n}"
    h = h.replace(a, b)

def swap_array(name, value):
    global h
    start = h.index(f"const {name} = ") + len(f"const {name} = ")
    end = h.index("\n]", start) + 2
    h = h[:start] + "[\n" + ",\n".join(json.dumps(x, ensure_ascii=False) for x in value) + "\n]" + h[end:]

# content
swap_array("WORDS", words)
swap_array("PROBLEMS", problems)
swap_array("FORMULAS", formulas)
rep('const MCATS = ["Number & Quantity", "Algebra", "Functions", "Geometry", "Statistics & Probability", "Essential Skills"];',
    "const MCATS = " + json.dumps(mcats, ensure_ascii=False) + ";")
start = h.index("const ENG=") + len("const ENG=")
end = h.index(";\nconst EKEY=", start)
h = h[:start] + json.dumps(eng, ensure_ascii=False) + h[end:]
rep('const ECATS=["Punctuation","Sentence Structure","Grammar & Usage","Style & Word Choice","Transitions & Organization"];',
    "const ECATS=" + json.dumps(ecats, ensure_ascii=False) + ";")
rep('const order=ch[0]==="NO CHANGE"?', 'const order=(ch[0]==="NO CHANGE"||ch[0]==="Correct as is")?')

# her own saved progress (never mixes with Yoseph's on a shared device)
for key in ["act-activity-v1", "act-eng-progress-v1", "act-last-sync", "act-math-progress-v1", "act-timed", "act-vocab-progress-v1"]:
    h = h.replace(f'"{key}"', f'"brooke-{key[4:]}"')
assert '"act-' not in h

# goal, sync, timer, labels
rep("const GOAL={days:7,cards:100,sets:3,acc:70,reward:25,dayMin:20};", "const GOAL={days:7,cards:60,sets:3,acc:70,reward:20,dayMin:15};")
rep('const SYNC_URL="/api/progress",SYNC_TOKEN="yoseph-act-sync-v1";', 'const SYNC_URL="/api/progress?student=brooke",SYNC_TOKEN="brooke-sync-v1";')
rep('const LETTERS=[["A","B","C","D"],["F","G","H","J"]];', 'const LETTERS=[["A","B","C","D"],["A","B","C","D"]];')
rep("const SEC={m:50*60/45,e:35*60/50};", "const SEC={m:90,e:60};")
rep("Timed (ACT pace)", "Timed challenge", 2)
h = h.replace("ACT pace is", "the challenge pace is")
rep('<option value="all">All ACT topics</option>', '<option value="all">All 6th-grade topics</option>')
rep("The ACT doesn't give you a formula sheet, so you need to know these.", "Know these formulas by heart.")
rep("`ACT Prep report (", "`Brooke's study report (")
rep("<title>ACT Vocab Drill</title>", "<title>Brooke's Study Quest</title>")
rep("<h1>ACT <span>Vocab</span> Drill</h1>", "<h1>Brooke's <span>Study</span> Quest</h1>")

# her palette: Aegean blue paper with laurel gold
h = h.replace("--paper:#eef3ee; --sheet:#fbfdfb; --ink:#1f2622; --muted:#5d6a63; --rule:#c9d6cd;",
              "--paper:#edf1fa; --sheet:#fbfcff; --ink:#1d2333; --muted:#5a6380; --rule:#c8d0e6;")
h = h.replace("--paper:#141a17; --sheet:#1c2420; --ink:#e7eee9; --muted:#9aaaa1; --rule:#2f3b35;",
              "--paper:#121626; --sheet:#1a2035; --ink:#e8ecf8; --muted:#9aa3c2; --rule:#2e3754;")
rep('<meta name="theme-color" content="#eef3ee">', '<meta name="theme-color" content="#edf1fa">')

out = root / "public/brooke/index.html"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(h)
print("wrote", out, len(h), "bytes;", len(words), "words,", len(problems), "math,", len(eng), "english")
