const $ = s => document.querySelector(s);
const $$ = s => document.querySelectorAll(s);

const toast = (msg) => {
  const el = $('#toast');
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 2400);
};

const observer = new IntersectionObserver(entries => {
  entries.forEach(e => { if(e.isIntersecting) e.target.classList.add('visible'); });
},{threshold:.12});
$$('.reveal').forEach(el => observer.observe(el));

$$('.chips button').forEach(btn => {
  btn.addEventListener('click', () => {
    $('#prompt').value = btn.dataset.prompt;
    $('#prompt').focus();
  });
});

function generateSite(){
  const text = $('#prompt').value.trim();
  if(!text){
    toast('✦ Сначала опиши свой сайт');
    $('#prompt').focus();
    return;
  }
  const lower = text.toLowerCase();
  let name = 'NOVA';
  let tag = 'DIGITAL EXPERIENCE';
  let title = 'Создаём<br><span>будущее.</span>';
  let desc = 'Современный цифровой опыт для твоего бизнеса.';

  if(lower.includes('авто') || lower.includes('машин') || lower.includes('автосалон')){
    name='MOTORX'; tag='PREMIUM AUTOMOTIVE'; title='Двигайся<br><span>быстрее.</span>'; desc='Автомобили, которым не нужны лишние слова.';
  } else if(lower.includes('ресторан') || lower.includes('еда') || lower.includes('кафе')){
    name='NOIR'; tag='FINE DINING'; title='Вкус, который<br><span>запомнят.</span>'; desc='Премиальная кухня и атмосфера в каждом блюде.';
  } else if(lower.includes('it') || lower.includes('стартап') || lower.includes('технолог')){
    name='NEXUS'; tag='NEXT GENERATION'; title='Build the<br><span>next.</span>'; desc='Технологии, которые превращают идеи в продукты.';
  } else if(lower.includes('спорт') || lower.includes('фитнес')){
    name='VOLT'; tag='PERFORMANCE'; title='Стань<br><span>сильнее.</span>'; desc='Тренировки и технологии для твоего лучшего результата.';
  }

  $('#siteName').textContent = name;
  $('#siteTag').textContent = tag;
  $('#siteTitle').innerHTML = title;
  $('#siteDesc').textContent = desc;
  $('#emptyState').style.display='none';
  $('#generated').style.display='block';
  toast('✓ AI создал макет сайта');
}

$('#generateBtn').addEventListener('click', generateSite);

$('#editBtn').addEventListener('click', () => {
  toast('✎ Редактор открыт — в полной версии здесь будет визуальный редактор');
});

$('#publishBtn').addEventListener('click', () => {
  toast('🚀 Проект подготовлен к публикации');
});

$('#loginBtn').addEventListener('click', () => toast('⌁ Авторизация будет подключена в backend-версии'));

$('#shuffleBtn').addEventListener('click', () => {
  const cards=[...$$('.template')];
  const parent=cards[0].parentElement;
  cards.sort(()=>Math.random()-.5).forEach(c=>parent.appendChild(c));
  toast('↻ Шаблоны перемешаны');
});

$('#prompt').addEventListener('keydown', e => {
  if((e.ctrlKey||e.metaKey)&&e.key==='Enter') generateSite();
});
