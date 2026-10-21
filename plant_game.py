from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

QUESTIONS = [
    ("أي هرمون يساعد على زيادة استطالة الساق؟",
     ["الأكسين","الجبرلينات","الإيثيلين","السيتوكينينات"], 1),
    ("أي هرمون يرتبط بنضج الثمار؟",
     ["الأكسين","الجبرلينات","الإيثيلين","السيتوكينينات"], 2),
    ("أي هرمون يرتبط بانقسام الخلايا وتكوين الأنسجة؟",
     ["السيتوكينينات","الإيثيلين","الأكسين","الجبرلينات"], 0),
    ("أي هرمون يرتبط باستطالة الخلايا والسيادة القمية؟",
     ["الإيثيلين","الأكسين","السيتوكينينات","الجبرلينات"], 1),
    ("نمو ساق النبات باتجاه مصدر الضوء يسمى:",
     ["الانتحاء الأرضي","الانتحاء اللمسي","الانتحاء الضوئي","الاستجابة الضوئية"], 2),
    ("نمو الجذر إلى أسفل استجابةً للجاذبية يسمى:",
     ["الانتحاء الضوئي","الانتحاء الأرضي","الانتحاء اللمسي","النمو القمي"], 1),
    ("التفاف نبات متسلق حول دعامة عند ملامستها مثال على:",
     ["الانتحاء الأرضي","الانتحاء الضوئي","الانتحاء اللمسي","النمو القمي"], 2),
    ("أي موقف يدل على تأثير الإيثيلين؟",
     ["زيادة نضج الثمرة","زيادة امتصاص الماء","زيادة تكوين الجذور فقط","توقف نمو الثمرة"], 0),
    ("من التأثيرات المرتبطة بالسيتوكينينات:",
     ["نضج الثمار","انقسام الخلايا وتكوين الأنسجة","الانتحاء الأرضي","الاستجابة للجاذبية"], 1),
    ("يتأثر تأثير الأكسين في النبات بـ:",
     ["تركيزه وموقع تأثيره","لون الأوراق فقط","كمية الماء فقط","عمر الثمرة فقط"], 0),
    ("إذا أعطي نباتان تراكيز مختلفة من الأكسين وظهرت استجابات نمو مختلفة، فما التفسير؟",
     ["الأكسين لا يؤثر في النمو","تأثير الأكسين يختلف حسب تركيزه وموقع تأثيره","جميع تراكيز الأكسين تعطي النتيجة نفسها","الاختلاف بسبب لون النبات"], 1),
    ("قالت طالبة: «كل استجابات النبات تعتبر حركات نمو». هل كلامها صحيح؟",
     ["نعم، جميعها مرتبطة بالنمو","لا، بعض الاستجابات تعتمد على مؤثر ولا ترتبط بالنمو الموضعي","نعم، لأن النبات لا يستجيب للمؤثرات","لا، لأن النباتات لا تتحرك"], 1)
]

HTML = r"""
<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>مهمة إنقاذ النبات 🌱</title>
<style>
body{margin:0;font-family:Tahoma,Arial;background:linear-gradient(135deg,#eef8ed,#fff9e8);color:#24402b}
.card{max-width:700px;margin:35px auto;background:white;padding:28px;border-radius:25px;box-shadow:0 8px 30px #0002}
h1{color:#387a45}.leaf{font-size:48px}
input{width:100%;box-sizing:border-box;padding:14px;border:2px solid #cfe4cf;border-radius:14px;font-size:17px;margin:12px 0}
button{width:100%;border:0;border-radius:14px;padding:14px;margin:7px 0;font-size:17px;cursor:pointer;background:#4f8f55;color:white}
.option{background:#f3f9f2;color:#24402b;border:2px solid #d8ead7;text-align:right}
.correct{background:#dff2df!important}.wrong{background:#fde3e3!important}
.hidden{display:none}.bar{height:10px;background:#e6efe5;border-radius:20px;overflow:hidden}
.fill{height:100%;background:#62a66a}.q{font-size:21px;font-weight:bold;line-height:1.7;margin:20px 0}
</style>
</head>
<body>
<div class="card">
<section id="start">
<div class="leaf">🌱🔬</div>
<h1>مهمة إنقاذ النبات</h1>
<p>اختبري معلوماتك عن هرمونات النبات واستجاباته.</p>
<p>12 سؤالًا • 10 درجات لكل سؤال • 5 دقائق</p>
<input id="name" placeholder="اكتبي اسمك">
<button onclick="start()">ابدئي التحدي 🚀</button>
</section>

<section id="game" class="hidden">
<div style="display:flex;justify-content:space-between">
<b id="num"></b><b id="time">05:00</b>
</div>
<div class="bar"><div id="fill" class="fill"></div></div>
<div id="q" class="q"></div>
<div id="opts"></div>
<p id="msg"></p>
<button id="next" class="hidden" onclick="next()">السؤال التالي ←</button>
</section>

<section id="result" class="hidden">
<div class="leaf">🏆🌿</div>
<h1>أحسنتِ!</h1>
<p id="who"></p>
<h2 id="score"></h2>
<h2 id="rank"></h2>
</section>
</div>

<script>
const data = {{ questions|tojson }};
let i=0, score=0, seconds=300, clock=null, answered=false;

function start(){
  const name=document.getElementById("name").value.trim();
  if(!name){alert("اكتبي اسمك أولًا 🌱");return;}
  document.getElementById("start").classList.add("hidden");
  document.getElementById("game").classList.remove("hidden");
  show();
  clock=setInterval(()=>{seconds--;timer();if(seconds<=0)finish()},1000);
}
function timer(){
  document.getElementById("time").textContent =
  String(Math.floor(seconds/60)).padStart(2,"0")+":"+String(seconds%60).padStart(2,"0");
}
function show(){
  answered=false;
  document.getElementById("num").textContent=`السؤال ${i+1} من ${data.length}`;
  document.getElementById("fill").style.width=(i/data.length*100)+"%";
  document.getElementById("q").textContent=data[i][0];
  document.getElementById("msg").textContent="";
  document.getElementById("next").classList.add("hidden");
  const box=document.getElementById("opts"); box.innerHTML="";
  data[i][1].forEach((text,n)=>{
    const b=document.createElement("button");
    b.className="option"; b.textContent=text;
    b.onclick=()=>answer(n,b); box.appendChild(b);
  });
}
function answer(n,b){
  if(answered)return; answered=true;
  const buttons=[...document.querySelectorAll(".option")];
  buttons.forEach(x=>x.disabled=true);
  if(n===data[i][2]){
    score+=10;b.classList.add("correct");
    document.getElementById("msg").textContent="إجابة صحيحة! ⭐ +10";
  }else{
    b.classList.add("wrong");
    buttons[data[i][2]].classList.add("correct");
    document.getElementById("msg").textContent="الإجابة الصحيحة موضحة بالأخضر 🌱";
  }
  document.getElementById("next").classList.remove("hidden");
}
function next(){
  i++;
  if(i>=data.length) finish(); else show();
}
function finish(){
  clearInterval(clock);
  document.getElementById("game").classList.add("hidden");
  document.getElementById("result").classList.remove("hidden");
  const name=document.getElementById("name").value.trim();
  document.getElementById("who").textContent="الطالبة: "+name;
  document.getElementById("score").textContent=`درجتك: ${score} من 120`;
  let rank=score>=110?"👑 عالمة نباتات محترفة!":
           score>=90?"🔬 باحثة نباتية متميزة!":
           score>=70?"🌱 مستكشفة عالم النبات!":
           "🌿 متدربة نباتية — أعيدي التحدي وارفعي مستواك!";
  document.getElementById("rank").textContent=rank;
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, questions=QUESTIONS)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
