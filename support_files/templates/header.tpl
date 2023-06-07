    <body class="vh-100 pa0 ma0 sans-serif roboto f4 fw6 dark-gray bg-near-white">
     <div id="page_container" class="relative min-h-100 overflow-hidden db">
        <div id="content_wrap" class="pb3">
            <div id="top-spacer" class="h4 mt0.5 mb4">
<nav id="navigation">
  <a href="http://localhost/{{ project }}/index.php" class="logo">{{ header_title }}<span>+<span></a>
  <ul class="links">
    <li><a href="http://localhost/{{ project }}/pages/about_page.php">About</a></li>
    <li class="dropdown"><a href="" class="trigger-drop">Stuff You Can Do<i class="arrow"></i></a>
      <ul class="drop">
 {% for list in lists %}
        <li><a href="http://localhost/{{ project }}/pages/{{ list[1] }}_page.php">{{ list[0] }}</a></li>
{% endfor %}
</ul>
    </li>
    <li class="dropdown"><a href="" class="trigger-drop">Contact<i class="arrow"></i></a>
      <ul class="drop">
        <li><a href="mailto:mclds@protonmail.com">Email</a></li>
        <li><a href="https://notabug.org/micaldas">Notabug</a></li>
      </ul>
    </li>
  </ul>
</nav>
</div>
<div id="bottom-spacer"></div>

