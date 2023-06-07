<!DOCTYPE html>
<html>
    <head>
    <title>{{ title }}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="author" content="Mclds">
    <meta name="description" content="{{ description }}">
    <meta property="og:type" content="web page">
    <meta property="og:url" content="{{ page_url }}">
    <link rel="stylesheet" type="text/css" href="http://localhost/{{ project }}/css/tachyons.css" media="screen">
    <link rel="stylesheet" type="text/css" href="http://localhost/{{ project }}/css/index.css" media="screen">
    <meta http-equiv="refresh" content="{{ refresh }}">
    </head>
    <?php include '/usr/share/nginx/html/support_services/partials/header.php'; ?>
      <div id="flex-container" class="flex mt=2 mb=2">
        <div id="col1" class="flex-row items-center self-center justify-center content-center w-10 order-0"></div>
        <div id="col2" class="flex-row items-center self-center justify-center content-center w-80 order-1">
            <div id='content'>{% block content %}
            {% endblock %}
        </div>
        <div id="col3" class="flex-row items-center self-center justify-center content-center w-10 order-2"></div>
<?php include '/usr/share/nginx/html/support_services/partials/footer.php'; ?>
</div>
  <script src="/new_rss/support_files/js/vendor/modernizr-3.11.2.min.js"></script>
  <script src="/new_rss/support_files/js/plugins.js"></script>
  <script src="/new_rss/support_files/js/main.js"></script>
</body>
</html>


