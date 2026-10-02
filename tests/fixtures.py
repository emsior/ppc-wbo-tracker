"""Small synthetic HTML fragments that mirror the markup of the PORTO ALEGRE platform.

They are hand-written (not copies of real pages) so the repository holds no platform content.
The editions menu deliberately leaves <li class="non-click"> unclosed, like the live page.
"""

PROJECTS_HTML = """
<html><head><title>Testowy Budżet Obywatelski 2027</title></head><body>
<p>Liczba projektów: 2</p>
<div class="project-item-content">
  <p class="project-status status-4">Wybrany&nbsp;do&nbsp;głosowania</p>
  <h2 class="title"><span class="project-nr">1.</span> <span>Ścieżka rowerowa nad rzeką </span></h2>
  <div class="additional-info">
    <p class="location"><span class="status">Obszar: </span>Nowe Miasto, Stary Zdrój</p>
    <p><span>Planowany koszt: </span>1&nbsp;009&nbsp;000&nbsp;zł</p>
  </div>
  <p class="desc "></p>
  <div class="see-more-button-wrapper"><a class="btn" href="https://example.test/projekt/34572">Zobacz szczegóły</a></div>
</div>
<div class="project-item-content">
  <p class="project-status status-realization">WYBRANY DO REALIZACJI</p>
  <h2 class="title"><span class="project-nr">2.</span> <span>Plac zabaw przy szkole</span></h2>
  <div class="additional-info">
    <p class="location"><span class="status">Obszar: </span></p>
    <p><span>Planowany koszt: </span>897&nbsp;340,05&nbsp;zł</p>
  </div>
  <div class="see-more-button-wrapper"><a class="btn" href="https://example.test/projekt/29485">Zobacz szczegóły</a></div>
</div>
</body></html>
"""

RESULTS_HTML = """
<html><body>
<div class="tr result-row win " data-project-id="29485">
  <div class="left-group"><div class="td nr f-center"><div class="mobile status-wrapper"><div class="status">Wybrany do realizacji</div></div>
  <span class="vote-label">Miejsce: </span> <span class="vote-position">1</span></div>
  <div class="td f-center"><div class="project-name"><span class="project-name-wrapper"><span class="project_nr">2.</span> <span>Plac zabaw przy szkole</span></span>
  <a class="btn" href="https://example.test/projekt/29485">Zobacz szczegóły</a></div></div></div>
  <div class="td details"><div><div class="status">Wybrany do realizacji</div></div><div class="td-inner votes">1&nbsp;438 <span class="votes-label">głosów</span></div>
  <div class="td-inner price"><span class="mobile inline">Koszt: </span>900&nbsp;000&nbsp;zł</div></div>
</div>
<div class="tr result-row " data-project-id="34572">
  <div class="left-group"><div class="td nr f-center"><span class="vote-label">Miejsce: </span> <span class="vote-position">2</span></div>
  <div class="td f-center"><div class="project-name"><span class="project-name-wrapper"><span class="project_nr">1.</span> <span>Ścieżka rowerowa nad rzeką</span></span></div></div></div>
  <div class="td details"><div><div class="status">Niezakwalifikowany</div></div><div class="td-inner votes">226 <span class="votes-label">głosów</span></div>
  <div class="td-inner price">893&nbsp;920&nbsp;zł</div></div>
</div>
<div id="stats-tab">
  <div class="info-graph info-graph-vote_persons"><h3>Liczba osób głosujących</h3><p class="additional-info">To wartość przedstawiająca ogólną frekwencję podczas głosowania.</p><div class="txtCount"><span class="timer" data-to="4928">0</span></div></div>
  <div class="info-graph info-graph-vote_persons"><h3>Liczba oddanych głosów</h3><p>Suma wszystkich głosów. Dotyczy tylko głosów ważnych.</p><div class="txtCount"><span class="timer" data-to="4928">0</span></div></div>
  <div class="info-graph info-graph-devices"><h3>Podział głosów:<br /> Komputery - Urządzenia mobilne</h3><p>Dotyczy tylko głosów ważnych.</p>
    <p class="subtitle">Komputery</p><div class="txtCount"><span class="timer" data-to="794">0</span> <span class="prc"><span class="timer" data-to="16.11">0</span>%</span></div>
    <p class="subtitle">Urządzenia mobilne</p><div class="txtCount"><span class="timer" data-to="4134">0</span><span class="prc"><span class="timer" data-to="83.89">0</span>%</span></div></div>
  <div class="info-graph info-graph-first-last-votes"><p class="subtitle">Pierwszy oddany głos</p><div class="txtCount mini">Poniedziałek, 1&nbsp;września&nbsp;2025&nbsp;00:01</div><p class="subtitle">Ostatni oddany głos</p><div class="txtCount mini">Wtorek, 30&nbsp;września&nbsp;2025&nbsp;23:32</div></div>
  <div class="info-graph info-graph-gender"><h3>Podział głosów: Kobiety - Mężczyźni</h3><p>Dotyczy tylko głosów ważnych.</p>
    <p class="subtitle">Kobiety</p><div class="txtCount"><span class="timer" data-to="2995">0</span><span class="prc"><span class="timer" data-to="60.78">0</span>%</span></div>
    <p class="subtitle">Mężczyźni</p><div class="txtCount"><span class="timer" data-to="1933">0</span><span class="prc"><span class="timer" data-to="39.22">0</span>%</span></div></div>
</div>
</body></html>
"""

EDITIONS_HTML = """
<html><body><ul class="main">
<li class="non-click"><span class="alike">Edycja 2026</span><ul class="submenu"><li><a href="https://example.test/poprzednie-edycje/11/projekty"><span>Zgłoszone projekty</span></a></li><li><a href="https://example.test/poprzednie-edycje/11/wyniki"><span>Wyniki</span></a></li></ul><li class="non-click"><span class="alike">Edycja 2025</span><ul class="submenu"><li><a href="https://example.test/poprzednie-edycje/10/aktualnosci"><span>Aktualności</span></a></li><li><a href="https://example.test/poprzednie-edycje/10/projekty"><span>Zgłoszone projekty</span></a></li></ul><li class="non-click"><span class="alike">Bez linku</span>
</ul></body></html>
"""

SCHEDULE_HTML = """
<html><body><div class="content">
<p>1. Zgłaszanie projektów do Budżetu Obywatelskiego</p>
<p>od 27.04.2026&nbsp;r. do 15.05.2026&nbsp;r.</p>
<p>3. Analiza projektów / <br><br>Rozpatrzenie odwołań</p>
<p>od 29.06.2026 r. <br><br>do 31.07.2026 r.</p>
<p>4. Głosowanie</p>
<p>od 01.09.2026 r. do 30.09.2026 r.</p>
<p>5. Oficjalne ogłoszenie wyników</p>
<p>do 15.10.2026 r.</p>
<p>6. Krok bez dat</p>
<p>Dodatkowe informacje</p>
</div></body></html>
"""
